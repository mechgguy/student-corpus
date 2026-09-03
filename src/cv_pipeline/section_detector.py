# src/cv_pipeline/section_detector.py

"""
Robust CV section detection.

Supports:
    - English CVs
    - German CVs
    - Mixed English/German CVs
    - PDF extraction artefacts / mojibake
    - headings containing additional descriptive words
    - headings with separators such as /, &, -, :, |

The detector intentionally produces canonical section names:

    summary
    experience
    education
    skills
    languages
    projects
    certifications
    awards
    activities

Anything not recognized remains attached to the current section.
"""

from __future__ import annotations

import re
import unicodedata

from .text_normalizer import (
    normalize_line,
    repair_mojibake
)


# ---------------------------------------------------------------------------
# Canonical section vocabulary
# ---------------------------------------------------------------------------

SECTION_PATTERNS: dict[str, list[str]] = {

    "summary": [
        # English
        r"summary",
        r"professional summary",
        r"profile",
        r"professional profile",
        r"personal profile",
        r"about me",
        r"about",
        r"objective",
        r"career objective",
        r"career summary",

        # German
        r"profil",
        r"persönliches profil",
        r"persoenliches profil",
        r"über mich",
        r"ueber mich",
        r"kurzprofil",
        r"berufsprofil",
        r"zielsetzung",
    ],

    "experience": [
        # English
        r"experience",
        r"work experience",
        r"professional experience",
        r"employment",
        r"employment history",
        r"career history",
        r"career",
        r"work history",
        r"professional background",
        r"work background",
        r"internship experience",
        r"professional experience and internships",
        r"experience and internships",

        # German
        r"berufserfahrung",
        r"berufliche erfahrung",
        r"beruflicher werdegang",
        r"beruflicher werdegang",
        r"praktische erfahrung",
        r"berufspraxis",
        r"beruflicher hintergrund",
        r"tätigkeiten",
        r"taetigkeiten",
        r"beschäftigung",
        r"beschaeftigung",
        r"werkstudententätigkeit",
        r"werkstudententaetigkeit",
        r"praktika",
        r"praktikum",
    ],

    "education": [
        # English
        r"education",
        r"educational background",
        r"academic background",
        r"academic education",
        r"academic qualifications",
        r"qualifications",
        r"studies",
        r"academic career",

        # German
        r"ausbildung",
        r"akademische ausbildung",
        r"akademischer werdegang",
        r"bildung",
        r"hochschulbildung",
        r"studium",
        r"schulbildung",
        r"schulischer werdegang",
        r"akademischer hintergrund",
    ],

    "skills": [
        # English
        r"skills",
        r"technical skills",
        r"technical expertise",
        r"technical knowledge",
        r"core competencies",
        r"competencies",
        r"competence",
        r"expertise",
        r"technologies",
        r"technology stack",
        r"tech stack",
        r"technical profile",
        r"tools",
        r"skills and tools",
        r"technical skills and tools",

        # German
        r"kenntnisse",
        r"fachkenntnisse",
        r"technische kenntnisse",
        r"technische fähigkeiten",
        r"technische faehigkeiten",
        r"fähigkeiten",
        r"faehigkeiten",
        r"kompetenzen",
        r"fachliche kompetenzen",
        r"technologien",
        r"technologie",
        r"techstack",
        r"technischer schwerpunkt",
    ],

    "languages": [
        # English
        r"languages",
        r"language skills",
        r"linguistic skills",
        r"foreign languages",
        r"language proficiency",

        # German
        r"sprachen",
        r"sprachkenntnisse",
        r"sprachkenntnisse und kompetenzen",
        r"fremdsprachen",
        r"sprachkompetenzen",
    ],

    "projects": [
        # English
        r"projects",
        r"project",
        r"personal projects",
        r"academic projects",
        r"selected projects",
        r"project experience",
        r"university projects",
        r"university project",
        r"research projects",
        r"research projects and publications",

        # German
        r"projekte",
        r"projekt",
        r"projekterfahrung",
        r"akademische projekte",
        r"universitätsprojekte",
        r"universitaetsprojekte",
        r"forschungsprojekte",
    ],

    "certifications": [
        # English
        r"certifications",
        r"certification",
        r"certificates",
        r"certificate",
        r"professional certifications",
        r"qualifications and certifications",
        r"certifications and awards",

        # German
        r"zertifikate",
        r"zertifikat",
        r"zertifizierungen",
        r"zertifizierung",
        r"weiterbildungen",
        r"weiterbildung",
        r"qualifikationen",
        r"zertifikate und leistungen",
        r"zertifikate und auszeichnungen",
    ],

    "awards": [
        # English
        r"awards",
        r"award",
        r"honors",
        r"honours",
        r"achievements",
        r"accomplishments",
        r"awards and achievements",
        r"honors and awards",
        r"awards and leadership",
        r"leadership and awards",

        # German
        r"auszeichnungen",
        r"auszeichnung",
        r"preise",
        r"preis",
        r"leistungen",
        r"ehrenamt",
        r"erfolge",
    ],

    "activities": [
        # English
        r"activities",
        r"extracurricular activities",
        r"volunteer activities",
        r"volunteering",
        r"leadership",
        r"engagement",
        r"extracurricular",
        r"social activities",

        # German
        r"engagement",
        r"ehrenamtliches engagement",
        r"ehrenamtliche tätigkeiten",
        r"ehrenamtliche taetigkeiten",
        r"soziales engagement",
        r"engagement und kompetenzen",
        r"engagement kompetenzen",
    ],
}


# ---------------------------------------------------------------------------
# Additional keyword groups
# ---------------------------------------------------------------------------
#
# These are deliberately broader than SECTION_PATTERNS.
# They allow headings such as:
#
#     Fähigkeiten / Techstack
#     Zertifikate und Leistungen
#     Engagement-Kompetenzen
#     Seminare-Präsentationen
#
# to be classified without having to enumerate every possible wording.
# ---------------------------------------------------------------------------

SECTION_KEYWORDS: dict[str, set[str]] = {

    "summary": {
        "summary",
        "profile",
        "profil",
        "about",
        "über mich",
        "ueber mich",
        "objective",
        "zielsetzung",
    },

    "experience": {
        "experience",
        "work",
        "employment",
        "career",
        "professional",
        "beruf",
        "berufserfahrung",
        "tätigkeiten",
        "taetigkeiten",
        "praktische",
        "praktikum",
        "praktika",
        "beschäftigung",
        "beschaeftigung",
        "werkstudent",
    },

    "education": {
        "education",
        "academic",
        "studies",
        "study",
        "school",
        "degree",
        "qualification",
        "education",
        "ausbildung",
        "studium",
        "bildung",
        "hochschulbildung",
        "schulbildung",
    },

    "skills": {
        "skills",
        "skill",
        "technical",
        "technologies",
        "technology",
        "expertise",
        "competencies",
        "competence",
        "kenntnisse",
        "fachkenntnisse",
        "fähigkeiten",
        "faehigkeiten",
        "kompetenzen",
        "techstack",
        "tech",
        "tools",
    },

    "languages": {
        "languages",
        "language",
        "linguistic",
        "sprachen",
        "sprachkenntnisse",
        "fremdsprachen",
    },

    "projects": {
        "projects",
        "project",
        "projekte",
        "projekt",
        "projekterfahrung",
        "research",
        "forschungsprojekte",
    },

    "certifications": {
        "certifications",
        "certification",
        "certificates",
        "certificate",
        "zertifikate",
        "zertifikat",
        "zertifizierungen",
        "weiterbildungen",
    },

    "awards": {
        "awards",
        "award",
        "honors",
        "honours",
        "achievements",
        "auszeichnungen",
        "preise",
        "leistungen",
        "erfolge",
    },

    "activities": {
        "activities",
        "leadership",
        "volunteering",
        "volunteer",
        "engagement",
        "ehrenamt",
        "aktivitäten",
        "aktivitaeten",
    },
}


# ---------------------------------------------------------------------------
# Mojibake repair
# ---------------------------------------------------------------------------

MOJIBAKE_REPLACEMENTS = {
    "Ã¤": "ä",
    "Ã¶": "ö",
    "Ã¼": "ü",
    "Ã„": "Ä",
    "Ã–": "Ö",
    "Ãœ": "Ü",
    "ÃŸ": "ß",

    "â€“": "-",
    "â€”": "-",
    "â€": "",
    "â€¢": " ",
    "Â·": " ",
    "Â": "",
    "ﬁ": "fi",
    "ﬂ": "fl",
}


def repair_mojibake(text: str) -> str:
    """
    Repair common UTF-8 -> Latin-1/Windows-1252 decoding artefacts.

    This is intentionally conservative. We only replace known artefacts
    instead of attempting aggressive re-encoding of the entire document.
    """

    if not text:
        return ""

    result = text

    for broken, fixed in MOJIBAKE_REPLACEMENTS.items():
        result = result.replace(broken, fixed)

    return result


# ---------------------------------------------------------------------------
# Heading normalization
# ---------------------------------------------------------------------------

def normalize_heading(line: str) -> str:
    """
    Normalize a potential section heading.

    Examples:

        "Fähigkeiten / Techstack"
            -> "fähigkeiten techstack"

        "Zertifikate und Leistungen"
            -> "zertifikate und leistungen"

        "Berufserfahrung P"
            -> "berufserfahrung p"

        "• WORK EXPERIENCE:"
            -> "work experience"
    """

    if not line:
        return ""

    value = repair_mojibake(line)

    value = unicodedata.normalize("NFKC", value)

    value = value.strip().lower()

    # Remove common PDF bullets / symbols / icons.
    value = re.sub(
        r"^[\s•·▪◦●○■□◆◇►▶→➜➤|]+",
        "",
        value,
    )

    # Replace common separators with spaces.
    value = re.sub(
        r"[/\\|&+:;,]+",
        " ",
        value,
    )

    # Hyphens inside headings are usually separators.
    value = re.sub(
        r"[-–—]+",
        " ",
        value,
    )

    # Remove remaining punctuation.
    value = re.sub(
        r"[^\w\säöüÄÖÜß]",
        " ",
        value,
        flags=re.UNICODE,
    )

    # Normalize German umlauts in alternative ASCII spelling.
    replacements = {
        "ä": "ä",
        "ö": "ö",
        "ü": "ü",
        "ß": "ß",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    # Collapse whitespace.
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ---------------------------------------------------------------------------
# Exact pattern detection
# ---------------------------------------------------------------------------

def _exact_match(normalized: str) -> str | None:
    """
    Check whether the complete normalized heading matches
    a known section pattern.
    """

    for section, patterns in SECTION_PATTERNS.items():

        for pattern in patterns:

            if re.fullmatch(
                pattern,
                normalized,
                re.IGNORECASE,
            ):
                return section

    return None


# ---------------------------------------------------------------------------
# Keyword-based detection
# ---------------------------------------------------------------------------

def _keyword_match(normalized: str) -> str | None:
    """
    Detect headings containing known section keywords.

    Example:

        "fähigkeiten techstack"
            -> skills

        "zertifikate und leistungen"
            -> certifications

        "engagement kompetenzen"
            -> activities

    Exact keyword matches receive priority over substring matches.
    """

    words = set(normalized.split())

    scores: dict[str, int] = {}

    for section, keywords in SECTION_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            keyword_words = set(keyword.split())

            # Exact phrase present.
            if keyword in normalized:
                score += 3

            # Individual keyword present.
            if keyword in words:
                score += 2

            # Multi-word keyword overlap.
            if len(keyword_words) > 1:
                overlap = len(words & keyword_words)

                if overlap:
                    score += overlap

        if score:
            scores[section] = score

    if not scores:
        return None

    # Highest score wins.
    best_section = max(
        scores,
        key=scores.get,
    )

    return best_section


# ---------------------------------------------------------------------------
# Heuristic detection
# ---------------------------------------------------------------------------

def _looks_like_heading(line: str) -> bool:
    """
    Determine whether a line is likely to be a section heading.

    This prevents ordinary CV sentences containing words such as
    "experience" or "skills" from accidentally becoming sections.
    """

    if not line:
        return False

    line = normalize_line(line)

    if not line:
        return False

    stripped = line.strip()

    if not stripped:
        return False

    # Very long lines are almost certainly body text.
    if len(stripped) > 100:
        return False

    words = stripped.split()

    # Section headings are usually short.
    if len(words) > 12:
        return False

    # Sentences with terminal punctuation are usually body text.
    if stripped.endswith((".", "!", "?")):
        return False

    return True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_section(line: str) -> str | None:
    """
    Detect a CV section from one line.

    Detection order:

        1. Exact heading match
        2. Keyword-based match
        3. Heuristic filtering

    Returns:
        canonical section name or None
    """

    if not line:
        return None

    if not _looks_like_heading(line):
        return None

    normalized = normalize_heading(line)

    if not normalized:
        return None

    # 1. Exact match.
    section = _exact_match(normalized)

    if section:
        return section

    # 2. Keyword match.
    section = _keyword_match(normalized)

    if section:
        return section

    return None


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

def split_sections(text: str) -> dict[str, str]:
    """
    Split CV text into canonical sections.

    Unknown content before the first recognized heading is stored
    under "header".

    Repeated section headings are merged automatically.
    """

    if not text:
        return {"header": ""}

    sections: dict[str, list[str]] = {
        "header": []
    }

    current_section = "header"

    for raw_line in text.splitlines():

        line = repair_mojibake(raw_line)

        detected = detect_section(line)

        if detected:

            current_section = detected

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections.setdefault(
            current_section,
            [],
        ).append(line)

    # Convert lists into strings.
    result = {}

    for section, lines in sections.items():

        cleaned_lines = []

        for line in lines:

            line = normalize_line(line)

            if not line:
                continue

            line = line.strip()

            if line:
                cleaned_lines.append(line)

        result[section] = "\n".join(
            cleaned_lines
        ).strip()

    return result
