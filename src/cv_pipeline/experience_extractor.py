from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


# ============================================================
# Configuration
# ============================================================

CURRENT_YEAR = date.today().year
CURRENT_MONTH = date.today().month


# ============================================================
# Date patterns
# ============================================================

MONTHS = {
    # English
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,

    # German
    "januar": 1,
    "jan": 1,
    "februar": 2,
    "märz": 3,
    "maerz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "okt": 10,
    "november": 11,
    "dezember": 12,
    "dez": 12,
}


PRESENT_WORDS = {
    "present",
    "current",
    "now",
    "ongoing",
    "today",

    # German
    "heute",
    "aktuell",
    "gegenwart",
    "laufend",
    "derzeit",
    "bis heute",
    "bis jetzt",
}


# ============================================================
# Section / semantic vocabulary
# ============================================================

EXPERIENCE_SECTION_NAMES = {
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "employment history",
    "career history",
    "work history",

    "berufserfahrung",
    "berufliche erfahrung",
    "arbeitserfahrung",
    "beruflicher werdegang",
    "beruflicher laufbahn",
    "beschäftigung",
    "beschaeftigung",
    "tätigkeiten",
    "taetigkeiten",
    "berufliche tätigkeiten",
    "berufliche taetigkeiten",
}


NON_EXPERIENCE_SECTION_NAMES = {
    # English
    "education",
    "academic background",
    "academic experience",
    "qualifications",
    "skills",
    "technical skills",
    "technical toolbox",
    "languages",
    "projects",
    "certifications",
    "certificates",
    "publications",
    "research",
    "awards",
    "honors",
    "interests",
    "volunteering",
    "social engagement",
    "references",
    "contact",
    "personal information",
    "personal info",
    "profile",
    "summary",
    "career goals",

    # German
    "ausbildung",
    "bildung",
    "studium",
    "akademischer werdegang",
    "qualifikationen",
    "kenntnisse",
    "fachkenntnisse",
    "fähigkeiten",
    "faehigkeiten",
    "technische kenntnisse",
    "sprachen",
    "projekte",
    "zertifikate",
    "zertifizierungen",
    "publikationen",
    "forschung",
    "auszeichnungen",
    "ehrenamt",
    "soziales engagement",
    "referenzen",
    "persönliche daten",
    "persoenliche daten",
    "persönliche informationen",
    "persoenliche informationen",
    "profil",
    "zusammenfassung",
    "karriereziele",
}


# ============================================================
# Job-title vocabulary
# ============================================================

JOB_TITLE_WORDS = {
    # English
    "engineer",
    "engineering",
    "developer",
    "software",
    "scientist",
    "researcher",
    "research",
    "analyst",
    "architect",
    "manager",
    "consultant",
    "specialist",
    "designer",
    "administrator",
    "technician",
    "intern",
    "trainee",
    "assistant",
    "associate",
    "coordinator",
    "director",
    "lead",
    "senior",
    "junior",
    "principal",
    "professor",
    "lecturer",
    "student",
    "working student",

    # German
    "ingenieur",
    "ingenieurin",
    "entwickler",
    "entwicklerin",
    "softwareentwickler",
    "softwareentwicklerin",
    "wissenschaftler",
    "wissenschaftlerin",
    "forscher",
    "forscherin",
    "analyst",
    "analystin",
    "architekt",
    "architektin",
    "manager",
    "berater",
    "beraterin",
    "spezialist",
    "spezialistin",
    "designer",
    "designerin",
    "techniker",
    "technikerin",
    "praktikant",
    "praktikantin",
    "werkstudent",
    "werkstudentin",
    "hilfskraft",
    "mitarbeiter",
    "mitarbeiterin",
    "assistent",
    "assistentin",
    "koordinator",
    "koordinatorin",
    "leiter",
    "leiterin",
    "leitung",
    "professor",
    "professorin",
    "dozent",
    "dozentin",
}


# ============================================================
# Education vocabulary
# ============================================================

EDUCATION_WORDS = {
    # English
    "bachelor",
    "master",
    "masters",
    "phd",
    "doctorate",
    "doctor",
    "degree",
    "university",
    "college",
    "school",
    "thesis",
    "dissertation",
    "student",

    # German
    "bachelor",
    "master",
    "promotion",
    "doktor",
    "doktorat",
    "universität",
    "universitaet",
    "hochschule",
    "fachhochschule",
    "studium",
    "studiert",
    "abschluss",
    "abschlussarbeit",
    "masterarbeit",
    "bachelorarbeit",
    "dissertation",
}


# ============================================================
# Description vocabulary
# ============================================================

DESCRIPTION_STARTERS = {
    # English
    "developed",
    "designed",
    "implemented",
    "created",
    "built",
    "worked",
    "working",
    "managed",
    "led",
    "supported",
    "maintained",
    "engineered",
    "programmed",
    "optimized",
    "analysed",
    "analyzed",
    "integrated",
    "deployed",
    "tested",
    "research",
    "researched",
    "responsible",
    "responsibilities",
    "contributed",
    "developing",
    "designing",
    "implementation",
    "development",

    # German
    "entwickelte",
    "entwickeln",
    "entwicklung",
    "implementierte",
    "implementierung",
    "konzipierte",
    "entwarf",
    "arbeitete",
    "betreute",
    "leitete",
    "unterstützte",
    "unterstuetzte",
    "wartete",
    "programmierte",
    "optimierte",
    "analysierte",
    "integrierte",
    "implementiert",
    "verantwortlich",
    "zuständig",
    "zustaendig",
    "mitarbeit",
    "mitwirkung",
    "durchführung",
    "durchfuehrung",
    "entwicklung",
}


# ============================================================
# Company indicators
# ============================================================

COMPANY_WORDS = {
    # English
    "gmbh",
    "ag",
    "kg",
    "mbh",
    "inc",
    "llc",
    "ltd",
    "corp",
    "corporation",
    "company",
    "university",
    "institute",
    "laboratory",
    "lab",
    "group",
    "solutions",
    "systems",
    "technologies",
    "technology",

    # German
    "unternehmen",
    "institut",
    "universität",
    "universitaet",
    "hochschule",
    "forschungszentrum",
    "zentrum",
    "werk",
}


# ============================================================
# Generic helpers
# ============================================================

def _clean(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    value = value.replace("\xa0", " ")
    value = value.strip()

    value = re.sub(
        r"^[\s:;,.|•●○\-–—]+",
        "",
        value,
    )

    value = re.sub(
        r"[\s:;,.|•●○\-–—]+$",
        "",
        value,
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip() or None


def _normalise_for_matching(value: str) -> str:
    value = _clean(value) or ""
    value = value.lower()

    # Handle common PDF encoding problems.
    replacements = {
        "â€“": "-",
        "â€”": "-",
        "âˆ’": "-",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "Ã¤": "ä",
        "Ã¶": "ö",
        "Ã¼": "ü",
        "ÃŸ": "ß",
        "Ã„": "ä",
        "Ã–": "ö",
        "Ãœ": "ü",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value.strip()


def _words(value: str) -> list[str]:
    return re.findall(
        r"[A-Za-zÄÖÜäöüßÀ-ÿ]+",
        _normalise_for_matching(value),
    )


def _contains_any_word(value: str, vocabulary: set[str]) -> bool:
    words = set(_words(value))
    return bool(words.intersection(vocabulary))


# ============================================================
# Date parsing
# ============================================================

@dataclass
class ParsedDate:
    year: int
    month: Optional[int]
    original: str


@dataclass
class DateRange:
    start: ParsedDate
    end: Optional[ParsedDate]
    original: str


def _valid_year(year: int) -> bool:
    return 1950 <= year <= CURRENT_YEAR + 2


def _parse_date_piece(value: str) -> Optional[ParsedDate]:
    """
    Parse one date component.

    Supported:
        2020
        03/2020
        03.2020
        03-2020
        March 2020
        März 2020
        2020-03
    """

    value = _normalise_for_matching(value)

    if not value:
        return None

    # YYYY-MM
    match = re.fullmatch(
        r"(19\d{2}|20\d{2})[-/.](0?[1-9]|1[0-2])",
        value,
    )

    if match:
        year = int(match.group(1))
        month = int(match.group(2))

        if _valid_year(year):
            return ParsedDate(
                year=year,
                month=month,
                original=value,
            )

    # MM-YYYY / MM.YYYY / MM/YYYY
    match = re.fullmatch(
        r"(0?[1-9]|1[0-2])[-/.](19\d{2}|20\d{2})",
        value,
    )

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if _valid_year(year):
            return ParsedDate(
                year=year,
                month=month,
                original=value,
            )

    # Month name + year
    match = re.fullmatch(
        r"([A-Za-zÄÖÜäöüß]+)\s+(19\d{2}|20\d{2})",
        value,
        re.IGNORECASE,
    )

    if match:
        month_name = match.group(1).lower()
        year = int(match.group(2))

        month = MONTHS.get(month_name)

        if month and _valid_year(year):
            return ParsedDate(
                year=year,
                month=month,
                original=value,
            )

    # Year + month name
    match = re.fullmatch(
        r"(19\d{2}|20\d{2})\s+([A-Za-zÄÖÜäöüß]+)",
        value,
        re.IGNORECASE,
    )

    if match:
        year = int(match.group(1))
        month_name = match.group(2).lower()

        month = MONTHS.get(month_name)

        if month and _valid_year(year):
            return ParsedDate(
                year=year,
                month=month,
                original=value,
            )

    # Year only
    match = re.fullmatch(
        r"(19\d{2}|20\d{2})",
        value,
    )

    if match:
        year = int(match.group(1))

        if _valid_year(year):
            return ParsedDate(
                year=year,
                month=None,
                original=value,
            )

    return None


def _is_present(value: str) -> bool:
    normalized = _normalise_for_matching(value)

    return normalized in PRESENT_WORDS


def _parse_date_range(line: str) -> Optional[DateRange]:
    """
    Extract an employment date range.

    Examples:

        2020 - 2022
        03/2020 - 09/2022
        March 2020 - Present
        März 2020 - heute
        2020 – heute
        2021 to 2023
        2021 bis 2023
    """

    line = _clean(line)

    if not line:
        return None

    # --------------------------------------------------------
    # Month-name dates
    # --------------------------------------------------------

    month_names = (
        r"January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|"
        r"Januar|Februar|März|Maerz|April|Mai|Juni|Juli|"
        r"August|September|Oktober|November|Dezember|Okt|Dez"
    )

    date_piece = (
        rf"(?:"
        rf"(?:{month_names})\s+(?:19\d{{2}}|20\d{{2}})"
        rf"|"
        rf"(?:19\d{{2}}|20\d{{2}})\s+(?:{month_names})"
        rf"|"
        rf"(?:0?[1-9]|1[0-2])[/.-](?:19\d{{2}}|20\d{{2}})"
        rf"|"
        rf"(?:19\d{{2}}|20\d{{2}})[/.-](?:0?[1-9]|1[0-2])"
        rf"|"
        rf"(?:19\d{{2}}|20\d{{2}})"
        rf")"
    )

    end_piece = rf"(?:{date_piece}|present|current|now|heute|aktuell|derzeit)"

    pattern = re.compile(
        rf"(?P<start>{date_piece})"
        rf"\s*"
        rf"(?:[-–—]|to|until|bis|bis\s+zum|–|—)"
        rf"\s*"
        rf"(?P<end>{end_piece})",
        re.IGNORECASE,
    )

    match = pattern.search(line)

    if match:

        start = _parse_date_piece(match.group("start"))

        if not start:
            return None

        end_text = match.group("end")

        if _is_present(end_text):
            end = ParsedDate(
                year=CURRENT_YEAR,
                month=CURRENT_MONTH,
                original=end_text,
            )
        else:
            end = _parse_date_piece(end_text)

        return DateRange(
            start=start,
            end=end,
            original=match.group(0),
        )

    # --------------------------------------------------------
    # "since 2020" / "seit 2020"
    # --------------------------------------------------------

    since_pattern = re.compile(
        rf"\b(?:since|from|seit|ab)\s+(?P<start>{date_piece})"
        rf"(?:\s*(?:-|–|—|to|until|bis)\s*"
        rf"(?P<end>{end_piece}))?",
        re.IGNORECASE,
    )

    match = since_pattern.search(line)

    if match:

        start = _parse_date_piece(match.group("start"))

        if not start:
            return None

        end_text = match.group("end")

        if end_text:
            if _is_present(end_text):
                end = ParsedDate(
                    CURRENT_YEAR,
                    CURRENT_MONTH,
                    end_text,
                )
            else:
                end = _parse_date_piece(end_text)
        else:
            end = ParsedDate(
                CURRENT_YEAR,
                CURRENT_MONTH,
                "present",
            )

        return DateRange(
            start=start,
            end=end,
            original=match.group(0),
        )

    return None


# ============================================================
# Date formatting
# ============================================================

def _format_date(value: ParsedDate) -> str:
    if value.month:
        return f"{value.year:04d}-{value.month:02d}"

    return f"{value.year:04d}"


def _date_to_month_index(value: ParsedDate) -> int:
    month = value.month or 1
    return value.year * 12 + month


def _calculate_duration(
    start: ParsedDate,
    end: Optional[ParsedDate],
) -> float:
    if not end:
        end = ParsedDate(
            CURRENT_YEAR,
            CURRENT_MONTH,
            "present",
        )

    start_index = _date_to_month_index(start)
    end_index = _date_to_month_index(end)

    months = max(
        0,
        end_index - start_index,
    )

    return round(months / 12.0, 2)


# ============================================================
# Line classification
# ============================================================

def _is_bullet(line: str) -> bool:
    return bool(
        re.match(
            r"^\s*(?:[-•●▪◦*►»]|[0-9]+[.)])\s+",
            line,
        )
    )


def _looks_like_section_heading(line: str) -> bool:
    normalized = _normalise_for_matching(line)

    if normalized in EXPERIENCE_SECTION_NAMES:
        return True

    if normalized in NON_EXPERIENCE_SECTION_NAMES:
        return True

    return False


def _looks_like_education(line: str) -> bool:
    return _contains_any_word(
        line,
        EDUCATION_WORDS,
    )


def _looks_like_job_title(line: str) -> bool:
    """
    Detect likely employment titles.

    Examples:
        Software Engineer
        Robotics Engineer
        Wissenschaftliche Hilfskraft
        Vertriebsmitarbeiterin
        Research Assistant
    """

    if not line:
        return False

    normalized = _normalise_for_matching(line)

    if _looks_like_section_heading(normalized):
        return False

    if _looks_like_education(line):
        return False

    return _contains_any_word(
        line,
        JOB_TITLE_WORDS,
    )


def _looks_like_company(line: str) -> bool:
    """
    Detect likely company / employer lines.
    """

    if not line:
        return False

    normalized = _normalise_for_matching(line)

    if _looks_like_section_heading(normalized):
        return False

    if _looks_like_job_title(line):
        return False

    if _contains_any_word(
        line,
        COMPANY_WORDS,
    ):
        return True

    # Common German company suffixes.
    if re.search(
        r"\b(?:GmbH|AG|KG|mbH|e\.V\.)\b",
        line,
        re.IGNORECASE,
    ):
        return True

    # Corporate suffixes in English.
    if re.search(
        r"\b(?:Inc\.?|LLC|Ltd\.?|Corp\.?)\b",
        line,
        re.IGNORECASE,
    ):
        return True

    return False


def _looks_like_location(line: str) -> bool:
    """
    Deliberately broad location detector.

    It does not maintain a hard-coded list of cities.
    """

    if not line:
        return False

    normalized = _normalise_for_matching(line)

    # Country indicators.
    if re.search(
        r"\b(?:Germany|Deutschland|Austria|Österreich|"
        r"Switzerland|Schweiz|France|Frankreich|"
        r"Netherlands|Niederlande|Belgium|Belgien|"
        r"United Kingdom|UK|USA|United States)\b",
        normalized,
        re.IGNORECASE,
    ):
        return True

    # City, country
    if re.search(
        r"^[A-Za-zÄÖÜäöüßÀ-ÿ .'-]+,\s*"
        r"[A-Za-zÄÖÜäöüßÀ-ÿ .'-]+$",
        line,
    ):
        return True

    # German postcode + city.
    if re.search(
        r"\b\d{5}\s+[A-Za-zÄÖÜäöüßÀ-ÿ .'-]+",
        line,
    ):
        return True

    # City + postcode.
    if re.search(
        r"^[A-Za-zÄÖÜäöüßÀ-ÿ .'-]+\s+\d{5}\b",
        line,
    ):
        return True

    return False


def _looks_like_description(line: str) -> bool:
    if not line:
        return False

    if _is_bullet(line):
        return True

    words = _words(line)

    if not words:
        return False

    first = words[0].lower()

    if first in DESCRIPTION_STARTERS:
        return True

    # Longer sentence-like lines are more likely descriptions.
    if len(words) >= 10:
        return True

    return False


def _looks_like_noise(line: str) -> bool:
    """
    Reject obvious PDF artefacts / decorative text.
    """

    if not line:
        return True

    stripped = line.strip()

    # Mostly symbols.
    alphanumeric = len(
        re.findall(
            r"[A-Za-zÄÖÜäöüßÀ-ÿ0-9]",
            stripped,
        )
    )

    if alphanumeric == 0:
        return True

    if len(stripped) <= 2:
        return True

    # Email / URL.
    if "@" in stripped:
        return True

    if re.search(
        r"https?://|www\.",
        stripped,
        re.IGNORECASE,
    ):
        return True

    return False


# ============================================================
# Candidate block
# ============================================================

@dataclass
class ExperienceCandidate:
    start: ParsedDate
    end: Optional[ParsedDate]

    position: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description_lines: list[str] | None = None

    score: float = 0.0
    date_line_index: int = -1

    def __post_init__(self):
        if self.description_lines is None:
            self.description_lines = []


# ============================================================
# Candidate scoring
# ============================================================

def _score_candidate(
    candidate: ExperienceCandidate,
) -> float:

    score = 0.0

    if candidate.start:
        score += 5

    if candidate.end:
        score += 2

    if candidate.position:
        score += 6

    if candidate.company:
        score += 5

    if candidate.location:
        score += 2

    if candidate.description_lines:
        score += min(
            4,
            len(candidate.description_lines),
        )

    # Position is particularly strong evidence.
    if candidate.position and _looks_like_job_title(
        candidate.position
    ):
        score += 5

    # Company is strong evidence.
    if candidate.company and _looks_like_company(
        candidate.company
    ):
        score += 4

    # Education-like candidates should be heavily penalized.
    combined = " ".join(
        filter(
            None,
            [
                candidate.position,
                candidate.company,
            ],
        )
    )

    if _looks_like_education(combined):
        score -= 8

    # Very long position/company lines are suspicious.
    if candidate.position and len(candidate.position) > 100:
        score -= 5

    if candidate.company and len(candidate.company) > 120:
        score -= 4

    return score


# ============================================================
# Build experience candidate around a date
# ============================================================

def _find_context_lines(
    lines: list[str],
    date_index: int,
    window: int = 6,
) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:

    before = []

    start = max(
        0,
        date_index - window,
    )

    for i in range(
        start,
        date_index,
    ):
        before.append(
            (
                i,
                lines[i],
            )
        )

    after = []

    end = min(
        len(lines),
        date_index + window + 1,
    )

    for i in range(
        date_index + 1,
        end,
    ):
        after.append(
            (
                i,
                lines[i],
            )
        )

    return before, after


def _select_position_and_company(
    context: list[tuple[int, str]],
    date_index: int,
) -> tuple[Optional[str], Optional[str]]:

    candidates = []

    for index, line in context:

        if _looks_like_noise(line):
            continue

        if _looks_like_section_heading(line):
            continue

        if _parse_date_range(line):
            continue

        if _looks_like_description(line):
            continue

        if _looks_like_location(line):
            continue

        position_score = 0

        if _looks_like_job_title(line):
            position_score += 10

        words = _words(line)

        if 1 <= len(words) <= 8:
            position_score += 2

        if len(line) <= 80:
            position_score += 1

        company_score = 0

        if _looks_like_company(line):
            company_score += 10

        if 1 <= len(words) <= 10:
            company_score += 1

        # Distance from date.
        distance = abs(
            index - date_index
        )

        position_score -= min(
            distance,
            4,
        ) * 0.5

        company_score -= min(
            distance,
            4,
        ) * 0.4

        candidates.append(
            (
                index,
                line,
                position_score,
                company_score,
            )
        )

    if not candidates:
        return None, None

    # --------------------------------------------------------
    # Position
    # --------------------------------------------------------

    position_candidates = sorted(
        candidates,
        key=lambda x: (
            -x[2],
            abs(x[0] - date_index),
        ),
    )

    position = None

    if position_candidates:
        best = position_candidates[0]

        if best[2] >= 3:
            position = best[1]

    # --------------------------------------------------------
    # Company
    # --------------------------------------------------------

    company_candidates = [
        item
        for item in candidates
        if item[1] != position
    ]

    company_candidates.sort(
        key=lambda x: (
            -x[3],
            abs(x[0] - date_index),
        )
    )

    company = None

    if company_candidates:
        best = company_candidates[0]

        if best[3] >= 3:
            company = best[1]

    return position, company


def _extract_description(
    lines: list[str],
    date_index: int,
    position: Optional[str],
    company: Optional[str],
    location: Optional[str],
) -> list[str]:

    description = []

    # Look primarily after the metadata.
    start = date_index + 1

    for i in range(
        start,
        min(
            len(lines),
            date_index + 12,
        ),
    ):

        line = lines[i]

        if _looks_like_section_heading(line):
            break

        if _parse_date_range(line):
            break

        if line in {
            position,
            company,
            location,
        }:
            continue

        if _looks_like_noise(line):
            continue

        # If another clear job title appears,
        # it probably starts another entry.
        if (
            _looks_like_job_title(line)
            and description
        ):
            break

        if _looks_like_description(line):
            description.append(line)
            continue

        # Bullet-free CV descriptions.
        if description:
            description.append(line)

        elif len(_words(line)) >= 8:
            description.append(line)

    return description


# ============================================================
# Main extraction
# ============================================================

def extract_experience(
    text: str,
) -> list[dict]:

    if not text or not text.strip():
        return []

    raw_lines = text.splitlines()

    lines = []

    for raw in raw_lines:

        line = _clean(raw)

        if not line:
            continue

        if _looks_like_noise(line):
            continue

        lines.append(line)

    if not lines:
        return []

    # --------------------------------------------------------
    # Find date ranges
    # --------------------------------------------------------

    date_candidates = []

    for index, line in enumerate(lines):

        parsed = _parse_date_range(line)

        if not parsed:
            continue

        date_candidates.append(
            (
                index,
                parsed,
            )
        )

    if not date_candidates:
        return []

    # --------------------------------------------------------
    # Build experience candidates
    # --------------------------------------------------------

    experiences: list[ExperienceCandidate] = []

    for date_index, date_range in date_candidates:

        before, after = _find_context_lines(
            lines,
            date_index,
        )

        context = before + after

        position, company = _select_position_and_company(
            context,
            date_index,
        )

        # Location.
        location = None

        for _, line in after:

            if _looks_like_location(line):
                location = line
                break

        # If no location after date, look before.
        if not location:

            for _, line in reversed(before):

                if _looks_like_location(line):
                    location = line
                    break

        description = _extract_description(
            lines,
            date_index,
            position,
            company,
            location,
        )

        candidate = ExperienceCandidate(
            start=date_range.start,
            end=date_range.end,
            position=position,
            company=company,
            location=location,
            description_lines=description,
            date_line_index=date_index,
        )

        candidate.score = _score_candidate(
            candidate
        )

        # ----------------------------------------------------
        # Require meaningful employment evidence.
        # ----------------------------------------------------

        if candidate.score < 8:
            continue

        # A date alone is not enough.
        if not position and not company:
            continue

        experiences.append(candidate)

    # --------------------------------------------------------
    # Remove duplicate candidates
    # --------------------------------------------------------

    unique = []

    seen = set()

    for candidate in experiences:

        key = (
            candidate.start.year,
            candidate.start.month,
            candidate.end.year if candidate.end else None,
            candidate.end.month if candidate.end else None,
            (candidate.position or "").lower(),
            (candidate.company or "").lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(candidate)

    experiences = unique

    # --------------------------------------------------------
    # Remove obvious education entries
    # --------------------------------------------------------

    filtered = []

    for candidate in experiences:

        combined = " ".join(
            filter(
                None,
                [
                    candidate.position,
                    candidate.company,
                    candidate.location,
                ],
            )
        )

        education_score = sum(
            1
            for word in _words(combined)
            if word in EDUCATION_WORDS
        )

        job_score = sum(
            1
            for word in _words(
                candidate.position or ""
            )
            if word in JOB_TITLE_WORDS
        )

        # Strong education signal + no job-title signal.
        if education_score >= 2 and job_score == 0:
            continue

        filtered.append(candidate)

    experiences = filtered

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    experiences.sort(
        key=lambda x: (
            x.start.year,
            x.start.month or 1,
        )
    )

    # --------------------------------------------------------
    # Convert to output schema
    # --------------------------------------------------------

    result = []

    for candidate in experiences:

        description = " ".join(
            candidate.description_lines or []
        )

        result.append(
            {
                "position": candidate.position,
                "company": candidate.company,
                "location": candidate.location,

                "start_date": _format_date(
                    candidate.start
                ),

                "end_date": (
                    _format_date(candidate.end)
                    if candidate.end
                    else None
                ),

                "description": (
                    description
                    if description
                    else None
                ),

                "duration_years": _calculate_duration(
                    candidate.start,
                    candidate.end,
                ),
            }
        )

    return result


# ============================================================
# Total experience
# ============================================================

def calculate_total_experience(
    experiences: list[dict],
) -> float:

    if not experiences:
        return 0.0

    intervals = []

    for experience in experiences:

        start_text = experience.get(
            "start_date"
        )

        end_text = experience.get(
            "end_date"
        )

        if not start_text:
            continue

        start = _parse_date_piece(
            start_text
        )

        if not start:
            continue

        if end_text:
            end = _parse_date_piece(
                end_text
            )
        else:
            end = ParsedDate(
                CURRENT_YEAR,
                CURRENT_MONTH,
                "present",
            )

        if not end:
            continue

        start_index = _date_to_month_index(
            start
        )

        end_index = _date_to_month_index(
            end
        )

        if end_index < start_index:
            continue

        intervals.append(
            (
                start_index,
                end_index,
            )
        )

    if not intervals:
        return 0.0

    # --------------------------------------------------------
    # Merge overlapping AND touching intervals.
    # --------------------------------------------------------

    intervals.sort()

    merged = []

    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:

        if start <= current_end + 1:

            current_end = max(
                current_end,
                end,
            )

        else:

            merged.append(
                (
                    current_start,
                    current_end,
                )
            )

            current_start = start
            current_end = end

    merged.append(
        (
            current_start,
            current_end,
        )
    )

    total_months = sum(
        end - start
        for start, end in merged
    )

    return round(
        total_months / 12.0,
        2,
    )