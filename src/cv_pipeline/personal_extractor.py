from __future__ import annotations

import re
from pathlib import Path


# =========================================================
# Generic cleaning
# =========================================================

def _clean(value):
    if not value:
        return None

    value = value.strip()

    # Fix common PDF / text extraction artefacts.
    value = re.sub(
        r"^[\s:;,.|\-–—â€“â€”]+",
        "",
        value,
    )

    value = re.sub(
        r"[\s:;,.|\-–—â€“â€”]+$",
        "",
        value,
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip() or None


# =========================================================
# Nationality
# =========================================================

NATIONALITY_PATTERNS = [
    re.compile(
        r"\b(?:nationality|citizenship)\s*[:\-]?\s*(.+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:nationalität|staatsangehörigkeit)\s*[:\-]?\s*(.+)",
        re.IGNORECASE,
    ),
]


def extract_nationality(text):
    """
    Extract nationality from a CV.
    """

    if not text:
        return None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        for pattern in NATIONALITY_PATTERNS:

            match = pattern.search(line)

            if not match:
                continue

            value = _clean(match.group(1))

            if value:
                return value

    return None


# =========================================================
# Name label
# =========================================================

NAME_LABEL_PATTERN = re.compile(
    r"^\s*(?:name|full name|vorname|nachname|"
    r"vollständiger name|vollstaendiger name)"
    r"\s*[:\-]\s*(.+)$",
    re.IGNORECASE,
)


# =========================================================
# Strong rejection phrases
# =========================================================

NAME_REJECT_PHRASES = {
    # CV / document
    "cv",
    "resume",
    "résumé",
    "curriculum vitae",
    "personal resume",
    "personal résumé",
    "personal cv",
    "lebenslauf",
    "Lebenslauf",
    "template",
    "cv template",
    "resume template",

    # Profile
    "profile",
    "my profile",
    "profile summary",
    "personal profile",
    "digital profile",
    "personal info",
    "personal information",
    "personal details",
    "personal data",
    "about me",

    # Contact
    "contact",
    "contact details",
    "contact information",
    "kontakt",
    "address",
    "adresse",

    # Sections
    "education",
    "ausbildung",
    "experience",
    "work experience",
    "berufserfahrung",
    "employment",
    "skills",
    "technical skills",
    "technical toolbox",
    "fähigkeiten",
    "faehigkeiten",
    "languages",
    "sprachen",
    "projects",
    "projekte",
    "certifications",
    "zertifikate",
    "references",
    "referenzen",
    "career goals",
    "career objective",
    "summary",

    # Online profiles
    "google scholar",
    "linkedin",
    "github",
    "portfolio",

    # Miscellaneous
    "service",
    "service cv",
    "service resume",
    "service profile",
}


# =========================================================
# Words that should NEVER occur in a name
# =========================================================

NAME_REJECT_WORDS = {
    # -----------------------------------------------------
    # CV / document
    # -----------------------------------------------------
    "cv",
    "resume",
    "résumé",
    "curriculum",
    "vitae",
    "template",
    "document",
    "application",
    "reference",

    # -----------------------------------------------------
    # Profile / sections
    # -----------------------------------------------------
    "profile",
    "summary",
    "personal",
    "info",
    "information",
    "details",
    "data",
    "contact",
    "kontakt",
    "about",

    "education",
    "ausbildung",
    "experience",
    "berufserfahrung",
    "employment",
    "skills",
    "technical",
    "toolbox",
    "languages",
    "sprachen",
    "projects",
    "projekte",
    "certifications",
    "zertifikate",
    "references",
    "referenzen",
    "career",
    "goals",
    "objective",

    # -----------------------------------------------------
    # Contact
    # -----------------------------------------------------
    "email",
    "phone",
    "mobile",
    "telefon",
    "nationality",
    "nationalität",
    "citizenship",
    "staatsangehörigkeit",
    "linkedin",
    "github",
    "portfolio",
    "website",
    "scholar",

    # -----------------------------------------------------
    # Education
    # -----------------------------------------------------
    "bachelor",
    "master",
    "masters",
    "doctor",
    "doctorate",
    "phd",
    "abitur",
    "diploma",
    "diplom",

    # -----------------------------------------------------
    # Job titles
    # -----------------------------------------------------
    "engineer",
    "engineering",
    "developer",
    "scientist",
    "researcher",
    "research",
    "assistant",
    "hilfskraft",
    "mitarbeiter",
    "mitarbeiterin",
    "student",
    "graduate",
    "manager",
    "consultant",
    "specialist",
    "architect",
    "analyst",
    "designer",
    "intern",
    "trainee",

    # -----------------------------------------------------
    # German job titles
    # -----------------------------------------------------
    "wissenschaftliche",
    "wissenschaftlicher",
    "wissenschaftliche",
    "studentische",
    "studentischer",
    "werkstudent",
    "werkstudentin",
    "praktikant",
    "praktikantin",
    "entwickler",
    "entwicklerin",
    "ingenieur",
    "ingenieurin",

    # -----------------------------------------------------
    # Professional / technical
    # -----------------------------------------------------
    "robotic",
    "robotics",
    "software",
    "computer",
    "vision",
    "data",
    "machine",
    "learning",
    "cloud",
    "devops",
    "mlops",

    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------
    "aachen",
    "berlin",
    "munich",
    "münchen",
    "hamburg",
    "frankfurt",
    "cologne",
    "köln",
    "germany",
    "deutschland",

    # -----------------------------------------------------
    # Generic words that frequently appear in filenames
    # -----------------------------------------------------
    "service",
    "services",
    "equipment",
    "design",
    "designer",
    "company",
    "career",
    "job",
    "jobs",
    "work",
    "working",
    "professional",
    "social",
    "engagement",
}


# =========================================================
# Location words
# =========================================================

LOCATION_WORDS = {
    "aachen",
    "berlin",
    "munich",
    "münchen",
    "hamburg",
    "frankfurt",
    "cologne",
    "köln",
    "germany",
    "deutschland",
    "herzogenrath",
}


# =========================================================
# Reject candidate
# =========================================================

def _looks_like_rejected_name(line):
    """
    Reject obvious non-name candidates.

    This deliberately does NOT use CV line numbers.
    """

    if not line:
        return True

    line = _clean(line)

    if not line:
        return True

    lower = line.lower().strip()

    # -----------------------------------------------------
    # Exact phrase rejection
    # -----------------------------------------------------

    if lower in NAME_REJECT_PHRASES:
        return True

    # -----------------------------------------------------
    # Wildcard / filename / template artefacts
    # -----------------------------------------------------

    if "*" in line:
        return True

    if "?" in line:
        return True

    if re.search(r"[{}\[\]<>]", line):
        return True

    # -----------------------------------------------------
    # URLs / email
    # -----------------------------------------------------

    if "@" in line:
        return True

    if re.search(
        r"(?:https?://|www\.)",
        line,
        re.IGNORECASE,
    ):
        return True

    # -----------------------------------------------------
    # Numeric information
    # -----------------------------------------------------

    if len(re.findall(r"\d", line)) > 1:
        return True

    # -----------------------------------------------------
    # Strong rejection words
    # -----------------------------------------------------

    words = re.findall(
        r"[A-Za-zÀ-ÿÄÖÜäöüß]+",
        lower,
    )

    for word in words:

        if word in NAME_REJECT_WORDS:
            return True

    # -----------------------------------------------------
    # Job title patterns
    # -----------------------------------------------------

    if re.search(
        r"\b(?:"
        r"engineer|engineering|developer|scientist|"
        r"researcher|assistant|hilfskraft|mitarbeiter|"
        r"manager|consultant|specialist|architect|"
        r"analyst|designer|student|graduate|intern|"
        r"trainee|wissenschaftliche|wissenschaftlicher|"
        r"studentische|studentischer|werkstudent|"
        r"praktikant|entwickler|ingenieur"
        r")\b",
        lower,
        re.IGNORECASE,
    ):
        return True

    # -----------------------------------------------------
    # Education patterns
    # -----------------------------------------------------

    if re.search(
        r"\b(?:"
        r"bachelor|master|masters|phd|doctorate|"
        r"diploma|diplom|abitur|m\.?\s*sc|b\.?\s*sc|"
        r"m\.?\s*eng|b\.?\s*eng"
        r")\b",
        lower,
        re.IGNORECASE,
    ):
        return True

    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------

    for location in LOCATION_WORDS:

        if re.search(
            rf"\b{re.escape(location)}\b",
            lower,
            re.IGNORECASE,
        ):
            return True

    return False


# =========================================================
# Name-like test
# =========================================================

def _looks_like_name(line):
    """
    Conservative test for a human name.

    This intentionally favors false negatives over
    accepting CV headings/job titles as names.
    """

    if not line:
        return False

    line = _clean(line)

    if not line:
        return False

    if _looks_like_rejected_name(line):
        return False

    # -----------------------------------------------------
    # Alphabetic content
    # -----------------------------------------------------

    if not re.search(r"[A-Za-zÀ-ÿÄÖÜäöüß]", line):
        return False

    # -----------------------------------------------------
    # Contact / URL
    # -----------------------------------------------------

    if "@" in line:
        return False

    if re.search(
        r"https?://|www\.",
        line,
        re.IGNORECASE,
    ):
        return False

    # -----------------------------------------------------
    # Numbers
    # -----------------------------------------------------

    if len(re.findall(r"\d", line)) > 1:
        return False

    # -----------------------------------------------------
    # Suspicious punctuation
    # -----------------------------------------------------

    punctuation = len(
        re.findall(
            r"[^A-Za-zÀ-ÿÄÖÜäöüß\s'.\-]",
            line,
        )
    )

    if punctuation > 1:
        return False

    # -----------------------------------------------------
    # Word count
    # -----------------------------------------------------

    words = line.split()

    if not 2 <= len(words) <= 5:
        return False

    # -----------------------------------------------------
    # Every word must be plausible as a name component.
    # -----------------------------------------------------

    name_word_pattern = re.compile(
        r"^[A-ZÀ-ÝÄÖÜ][A-Za-zÀ-ÿÄÖÜäöüß'’\-]*$"
    )

    capitalized_words = sum(
        1
        for word in words
        if name_word_pattern.fullmatch(word)
    )

    # At least two properly capitalized components.
    if capitalized_words < 2:
        return False

    # -----------------------------------------------------
    # Sentence-like words
    # -----------------------------------------------------

    common_sentence_words = {
        "and",
        "or",
        "the",
        "with",
        "for",
        "from",
        "to",
        "of",
        "in",
        "on",
        "a",
        "an",
        "und",
        "oder",
        "mit",
        "für",
        "von",
        "zu",
        "der",
        "die",
        "das",
    }

    if any(
        word.lower() in common_sentence_words
        for word in words
    ):
        return False

    # -----------------------------------------------------
    # Sentence punctuation
    # -----------------------------------------------------

    if line.endswith(
        (".", ":", ";", "!", "?", ",")
    ):
        return False

    return True


# =========================================================
# Name scoring
# =========================================================

def _name_score(line, index):
    """
    Score a plausible name.

    Position is only a weak signal.
    """

    if not _looks_like_name(line):
        return -999

    words = line.split()

    score = 0

    # Two-word names are very common.
    if len(words) == 2:
        score += 8

    elif len(words) == 3:
        score += 7

    elif len(words) == 4:
        score += 4

    else:
        score += 2

    # Proper capitalization.
    capitalized = sum(
        1
        for word in words
        if word[:1].isupper()
    )

    if capitalized == len(words):
        score += 5

    elif capitalized >= 2:
        score += 2

    # Early occurrence is useful but not required.
    if index < 5:
        score += 2

    elif index < 15:
        score += 1

    return score


# =========================================================
# Filename name extraction
# =========================================================

def _filename_tokens(filename):
    """
    Convert a filename into candidate tokens.

    Examples:

        Max_Mustermann_CV.pdf
        Max Mustermann Resume.pdf
        Max-Mustermann.pdf

    become:

        ["Max", "Mustermann", "CV"]
    """

    if not filename:
        return []

    name = Path(str(filename)).stem

    # Replace separators with spaces.
    name = re.sub(
        r"[_\-+.]+",
        " ",
        name,
    )

    # Remove brackets but preserve words.
    name = re.sub(
        r"[()\[\]{}]",
        " ",
        name,
    )

    name = re.sub(r"\s+", " ", name).strip()

    if not name:
        return []

    return name.split()


def extract_name_from_filename(filename):
    """
    Try to extract a person's name from the filename.

    Filename detection has intentionally strict rules.

    Examples accepted:

        Max_Mustermann.pdf
        Max Mustermann_CV.pdf
        Anna-Schmidt_Resume.pdf

    Examples rejected:

        CV_Template.pdf
        Service_CV.pdf
        Robot_Design.pdf
        Aachen_CV.pdf
        CV_2025.pdf
    """

    if not filename:
        return None

    tokens = _filename_tokens(filename)

    if not tokens:
        return None

    # Remove obvious filename metadata from the END.
    removable_words = {
        "cv",
        "CV",
        "resume",
        "résumé",
        "lebenslauf",
        "Lebenslauf",
        "curriculum",
        "vitae",
        "template",
        "application",
        "profile",
        "personal",
        "final",
        "updated",
        "latest",
        "new",
        "version",
        "copy",
        "draft",
        "bewerbung",
        "anschreiben",
    }

    while tokens and tokens[-1].lower() in removable_words:
        tokens.pop()

    if len(tokens) < 2:
        return None

    # -----------------------------------------------------
    # Try the complete remaining filename.
    # -----------------------------------------------------

    candidate = " ".join(tokens)

    if _looks_like_name(candidate):
        return candidate

    # -----------------------------------------------------
    # Try pairs.
    #
    # This handles:
    #
    #   Max_Mustermann_CV
    #   Max_Mustermann_Resume
    #
    # without assuming where the name is.
    # -----------------------------------------------------

    pair_candidates = []

    for i in range(len(tokens) - 1):

        pair = " ".join(
            tokens[i:i + 2]
        )

        if _looks_like_name(pair):

            score = 0

            # Strong preference for beginning of filename.
            if i == 0:
                score += 5

            # Penalize candidates surrounded by obvious
            # metadata words.
            surrounding = []

            if i > 0:
                surrounding.append(
                    tokens[i - 1].lower()
                )

            if i + 2 < len(tokens):
                surrounding.append(
                    tokens[i + 2].lower()
                )

            if any(
                word in removable_words
                or word in NAME_REJECT_WORDS
                for word in surrounding
            ):
                score -= 3

            score += 10

            pair_candidates.append(
                (
                    score,
                    i,
                    pair,
                )
            )

    if not pair_candidates:
        return None

    pair_candidates.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return pair_candidates[0][2]


# =========================================================
# Name extraction from CV text
# =========================================================

def extract_name(text):
    """
    Extract a person's name from CV text.

    Strategy:

        1. Explicit Name: field.
        2. Adjacent short name lines.
        3. Multi-word candidates.
        4. Scoring.

    No fixed CV line number is used.
    """

    if not text:
        return None

    lines = []

    for raw_line in text.splitlines():

        line = _clean(raw_line)

        if line:
            lines.append(line)

    if not lines:
        return None

    # -----------------------------------------------------
    # 1. Explicit Name: field
    # -----------------------------------------------------

    for line in lines:

        match = NAME_LABEL_PATTERN.match(line)

        if not match:
            continue

        candidate = _clean(
            match.group(1)
        )

        if (
            candidate
            and _looks_like_name(candidate)
        ):
            return candidate

    # -----------------------------------------------------
    # 2. Candidate combinations
    # -----------------------------------------------------

    candidates = []

    for index, line in enumerate(lines):

        # -------------------------------------------------
        # Single-line candidate
        # -------------------------------------------------

        score = _name_score(
            line,
            index,
        )

        if score > 0:

            candidates.append(
                (
                    score,
                    index,
                    line,
                )
            )

        # -------------------------------------------------
        # Adjacent lines
        #
        # Example:
        #
        #   Max
        #   Mustermann
        #
        # becomes:
        #
        #   Max Mustermann
        # -------------------------------------------------

        if index + 1 < len(lines):

            next_line = lines[index + 1]

            if (
                len(line.split()) <= 2
                and len(next_line.split()) <= 2
            ):

                combined = (
                    f"{line} {next_line}"
                )

                if _looks_like_name(
                    combined
                ):

                    combined_score = (
                        _name_score(
                            combined,
                            index,
                        )
                        + 4
                    )

                    candidates.append(
                        (
                            combined_score,
                            index,
                            combined,
                        )
                    )

    # -----------------------------------------------------
    # Select best candidate
    # -----------------------------------------------------

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return candidates[0][2]