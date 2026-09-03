import re


# =========================================================
# Date parsing
# =========================================================

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
    "november": 11,
    "dezember": 12,
}


# =========================================================
# Date patterns
# =========================================================

MONTH_NAME_PATTERN = (
    r"[A-Za-zäöüÄÖÜß]+"
)

DATE_TOKEN = rf"""
(?:
    \d{{1,2}}[/-]\d{{4}}
    |
    \d{{4}}[/-]\d{{1,2}}
    |
    \d{{4}}
    |
    {MONTH_NAME_PATTERN}\s+\d{{4}}
)
"""

DATE_RANGE_PATTERN = re.compile(
    rf"""
    (?P<start>{DATE_TOKEN})
    \s*
    (?:
        -
        |
        –
        |
        —
        |
        to
        |
        bis
        |
        until
    )
    \s*
    (?P<end>
        {DATE_TOKEN}
        |
        Present
        |
        Current
        |
        Ongoing
        |
        Now
        |
        Heute
        |
        Aktuell
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

SINCE_PATTERN = re.compile(
    rf"""
    \b
    (?:
        since
        |
        seit
    )
    \s+
    (?P<date>{DATE_TOKEN})
    """,
    re.IGNORECASE | re.VERBOSE,
)


# =========================================================
# Date parsing
# =========================================================

def parse_date(value):
    if not value:
        return None

    value = value.strip()
    value = value.rstrip(":;,.")
    value = re.sub(r"\s+", " ", value)

    # MM/YYYY
    match = re.fullmatch(
        r"(\d{1,2})[/-](\d{4})",
        value,
    )

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}"

    # YYYY/MM or YYYY-MM
    match = re.fullmatch(
        r"(\d{4})[/-](\d{1,2})",
        value,
    )

    if match:
        year = int(match.group(1))
        month = int(match.group(2))

        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}"

    # YYYY
    if re.fullmatch(r"\d{4}", value):
        return f"{int(value):04d}-01"

    # Month YYYY
    match = re.fullmatch(
        rf"({MONTH_NAME_PATTERN})\s+(\d{{4}})",
        value,
        re.IGNORECASE,
    )

    if match:
        month_name = match.group(1).lower()
        year = int(match.group(2))

        month = MONTHS.get(month_name)

        if month:
            return f"{year:04d}-{month:02d}"

    return None


def _extract_dates(line):
    if not line:
        return None, None

    match = DATE_RANGE_PATTERN.search(line)

    if match:

        start = parse_date(
            match.group("start")
        )

        end_value = match.group("end")

        if re.fullmatch(
            r"(present|current|ongoing|now|heute|aktuell)",
            end_value,
            re.IGNORECASE,
        ):
            end = None
        else:
            end = parse_date(end_value)

        return start, end

    match = SINCE_PATTERN.search(line)

    if match:

        start = parse_date(
            match.group("date")
        )

        return start, None

    return None, None


def _is_date_line(line):
    start, end = _extract_dates(line)

    return (
        start is not None
        or end is not None
    )


# =========================================================
# Cleaning
# =========================================================

def _clean_line(line):
    if not line:
        return ""

    line = line.strip()

    # PDF bullet artifacts
    line = re.sub(
        r"^[\uf0b7\u2022\u25cf\u25aa]+\s*",
        "",
        line,
    )

    # Broken dash encoding / line wrapping
    line = line.replace("??", "–")

    # Remove page-number-only lines
    if re.fullmatch(r"\d+", line):
        return ""

    # Excessive whitespace
    line = re.sub(
        r"\s+",
        " ",
        line,
    )

    return line.strip()


def _clean_field(value):
    if not value:
        return None

    value = value.strip()

    value = re.sub(
        r"^[\s:;,.–—-]+",
        "",
        value,
    )

    value = re.sub(
        r"[\s:;,.]+$",
        "",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip() or None


def _normalize_lines(text):
    if not text:
        return []

    lines = []

    for line in text.splitlines():

        line = _clean_line(line)

        if line:
            lines.append(line)

    return lines


# =========================================================
# Grade extraction
# =========================================================

GRADE_PATTERNS = [

    re.compile(
        r"\bNote\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bGrade\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bGPA\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bCGPA\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bGesamtnote\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\b"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"\s*/\s*[0-9]+)"
        r"\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\b"
        r"([0-9]+(?:[.,][0-9]+)?\s*%)"
        r"\b",
        re.IGNORECASE,
    ),
]


def _extract_grade(lines):

    grade = None
    cleaned_lines = []

    for line in lines:

        current = line

        for pattern in GRADE_PATTERNS:

            match = pattern.search(current)

            if not match:
                continue

            if grade is None:
                grade = (
                    match.group(1)
                    .replace(",", ".")
                    .strip()
                )

            current = pattern.sub(
                "",
                current,
            )

            break

        current = _clean_field(current)

        if current:
            cleaned_lines.append(current)

    return grade, cleaned_lines


# =========================================================
# Institution detection
# =========================================================

INSTITUTION_INDICATORS = (
    "university",
    "universität",
    "universitaet",
    "hochschule",
    "rwth",
    "school",
    "schule",
    "gymnasium",
    "college",
    "institute",
    "institut",
    "universidade",
    "technical university",
    "technische universität",

    # Common institutional abbreviations.
    # These are checked as words, not arbitrary substrings.
    "iit",
    "bit",
)


def _looks_like_institution(line):
    if not line:
        return False

    lower = line.lower().strip()

    # Full institution names.
    full_indicators = (
        "university",
        "universität",
        "universitaet",
        "hochschule",
        "rwth",
        "school",
        "schule",
        "gymnasium",
        "college",
        "institute",
        "institut",
        "universidade",
        "technical university",
        "technische universität",
    )

    if any(
        indicator in lower
        for indicator in full_indicators
    ):
        return True

    # Short institutional abbreviations must be
    # complete tokens / abbreviations.
    if re.search(
        r"\bIIT\b",
        line,
        re.IGNORECASE,
    ):
        return True

    if re.search(
        r"\bBIT(?:\s|-|$)",
        line,
        re.IGNORECASE,
    ):
        return True

    return False


def _extract_institution(lines):

    for line in lines:

        if _looks_like_institution(line):

            return _clean_field(line)

    return None


# =========================================================
# Degree detection
# =========================================================

DEGREE_PATTERNS = [

    re.compile(
        r"\bB\.?\s*Sc\.?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bM\.?\s*Sc\.?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bB\.?\s*Eng\.?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bM\.?\s*Eng\.?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bBachelor\s+of\s+Engineering\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bBachelor\s+of\s+Science\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bMaster\s+of\s+Engineering\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bMaster\s+of\s+Science\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bBachelor\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bMaster\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bDiplom\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bAbitur\b",
        re.IGNORECASE,
    ),
]


def _is_degree_line(line):
    if not line:
        return False

    return any(
        pattern.search(line)
        for pattern in DEGREE_PATTERNS
    )


def _normalize_degree(value):

    if not value:
        return None

    value = value.strip()

    normalized = re.sub(
        r"[\s.]",
        "",
        value.lower(),
    )

    mapping = {

        "bsc": "B.Sc",
        "msc": "M.Sc",
        "beng": "B.Eng",
        "meng": "M.Eng",

        "bachelorofengineering":
            "B.Eng",

        "bachelorofscience":
            "B.Sc",

        "masterofengineering":
            "M.Eng",

        "masterofscience":
            "M.Sc",

        "bachelor":
            "Bachelor",

        "master":
            "Master",

        "diplom":
            "Diplom",

        "abitur":
            "Abitur",
    }

    return mapping.get(
        normalized,
        _clean_field(value),
    )


# =========================================================
# Degree + field parsing
# =========================================================

def _parse_degree_field(text):

    if not text:
        return None, None

    text = _clean_field(text)

    # Remove institution after "at".
    text_without_institution = re.sub(
        r"\s+\bat\s+.+$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text_without_institution = _clean_field(
        text_without_institution
    )

    # Abitur
    if re.search(
        r"\bAbitur\b",
        text,
        re.IGNORECASE,
    ):
        return "Abitur", None

    # Full Bachelor/Master ... in FIELD
    match = re.search(
        r"\b("
        r"Master\s+of\s+Science"
        r"|Master\s+of\s+Engineering"
        r"|Bachelor\s+of\s+Science"
        r"|Bachelor\s+of\s+Engineering"
        r"|Master"
        r"|Bachelor"
        r")"
        r"\s+in\s+(.+)",
        text_without_institution,
        re.IGNORECASE,
    )

    if match:

        degree = _normalize_degree(
            match.group(1)
        )

        field = _clean_field(
            match.group(2)
        )

        return degree, field

    degree_match = None

    sorted_patterns = sorted(
        DEGREE_PATTERNS,
        key=lambda pattern: len(pattern.pattern),
        reverse=True,
    )

    for pattern in sorted_patterns:

        match = pattern.search(
            text_without_institution
        )

        if match:

            degree_match = match
            break

    if not degree_match:
        return None, None

    degree = _normalize_degree(
        degree_match.group(0)
    )

    before = _clean_field(
        text_without_institution[
            :degree_match.start()
        ]
    )

    after = _clean_field(
        text_without_institution[
            degree_match.end():
        ]
    )

    if before:
        field = before

    elif after:
        field = after

    else:
        field = None

    return degree, _clean_field(field)


# =========================================================
# Institution extraction from academic text
# =========================================================

def _split_at_institution(text):

    if not text:
        return text, None

    # "Degree at UNIVERSITY"
    match = re.search(
        r"\s+\bat\s+(.+)$",
        text,
        re.IGNORECASE,
    )

    if match:

        academic_part = text[
            :match.start()
        ]

        institution = match.group(1)

        return (
            _clean_field(academic_part),
            _clean_field(institution),
        )

    # "Degree, UNIVERSITY"
    parts = re.split(
        r"\s*,\s*",
        text,
    )

    if len(parts) >= 2:

        for i in range(1, len(parts)):

            right = ", ".join(
                parts[i:]
            )

            if _looks_like_institution(right):

                left = ", ".join(
                    parts[:i]
                )

                return (
                    _clean_field(left),
                    _clean_field(right),
                )

    return text, None


# =========================================================
# Non-core education information
# =========================================================

NON_CORE_PATTERNS = (
    "relevant courses",
    "relevant modules",
    "relevant coursework",
    "schwerpunkte",
    "fachrichtungen",
    "wahlfächer",
    "wahlfaecher",
    "wahlfach",
    "electives",
    "elective courses",
    "expected graduation",
    "expected completion",
    "voraussichtlicher abschluss",
    "voraussichtlicher",
    "coursework",
    "vertiefende studie",
    "vertiefende studien",
    "deutsch-äquivalent",
    "deutsch-aequivalent",
)


def _is_non_core_line(line):

    if not line:
        return False

    lower = line.lower()

    return any(
        pattern in lower
        for pattern in NON_CORE_PATTERNS
    )


def _remove_non_core_text(text):

    if not text:
        return text

    # Remove everything starting from supplementary
    # education information.
    text = re.split(
        r"\bVertiefende\s+Studie\s*:",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    text = re.split(
        r"\bWahlfächer\s*:",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    text = re.split(
        r"\bWahlfaecher\s*:",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    text = re.split(
        r"\bElective\s+Courses?\s*:",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    return _clean_field(text)


# =========================================================
# Institution cleanup
# =========================================================

def _clean_institution(institution):

    if not institution:
        return None

    institution = _clean_field(
        institution
    )

    if not institution:
        return None

    institution = re.sub(
        r"^(Bachelor|Master|Master of Science|"
        r"Master of Engineering|Bachelor of Science|"
        r"Bachelor of Engineering)\s*,?\s*",
        "",
        institution,
        flags=re.IGNORECASE,
    )

    return _clean_field(institution)


# =========================================================
# Candidate construction
# =========================================================

def _build_candidate(
    lines,
    start_date,
    end_date,
):

    if not lines:
        return None

    # Remove date lines.
    lines = [
        line
        for line in lines
        if not _is_date_line(line)
    ]

    # -----------------------------------------------------
    # Remove supplementary lines.
    #
    # IMPORTANT:
    # Once a non-core line starts, its continuation lines
    # are also ignored until the next meaningful academic
    # entry.
    # -----------------------------------------------------

    cleaned_lines = []

    skip_continuation = False

    for line in lines:

        if _is_non_core_line(line):

            skip_continuation = True
            continue

        if skip_continuation:

            # A new strong academic line ends the
            # supplementary section.
            if (
                _looks_like_institution(line)
                or _is_degree_line(line)
                or re.search(
                    r"\bengineering\b|\bscience\b",
                    line,
                    re.IGNORECASE,
                )
            ):
                skip_continuation = False
            else:
                continue

        cleaned_lines.append(line)

    lines = cleaned_lines

    if not lines:
        return None

    # -----------------------------------------------------
    # Grade
    # -----------------------------------------------------

    grade, lines = _extract_grade(
        lines
    )

    if not lines:
        return None

    # -----------------------------------------------------
    # Remove supplementary information that may remain
    # on the same line as the actual field.
    # -----------------------------------------------------

    lines = [
        _remove_non_core_text(line)
        for line in lines
    ]

    lines = [
        line
        for line in lines
        if line
    ]

    if not lines:
        return None

    # -----------------------------------------------------
    # Institution
    # -----------------------------------------------------

    institution = None
    academic_lines = []

    for line in lines:

        academic_part, explicit_institution = (
            _split_at_institution(line)
        )

        if explicit_institution:

            institution = (
                _clean_institution(
                    explicit_institution
                )
            )

            if academic_part:
                academic_lines.append(
                    academic_part
                )

            continue

        if _looks_like_institution(line):

            if institution is None:
                institution = (
                    _clean_institution(line)
                )

            continue

        academic_lines.append(line)

    # -----------------------------------------------------
    # If no institution found yet, search all lines.
    # -----------------------------------------------------

    if not institution:

        institution = _extract_institution(
            lines
        )

        institution = _clean_institution(
            institution
        )

        if institution:

            academic_lines = [
                line
                for line in academic_lines
                if line != institution
            ]

    # -----------------------------------------------------
    # Academic text
    # -----------------------------------------------------

    academic_text = _clean_field(
        " ".join(academic_lines)
    )

    # -----------------------------------------------------
    # Remove country/location leakage from the beginning
    # of degree fields.
    #
    # Example:
    #   Bachelor of Engineering, Indien
    #
    # should not result in:
    #   Indien Mechanical Engineering
    # -----------------------------------------------------

    if academic_text:

        academic_text = re.sub(
            r"^(?:Indien|India|Deutschland|Germany)"
            r"\s+",
            "",
            academic_text,
            flags=re.IGNORECASE,
        )

        academic_text = _clean_field(
            academic_text
        )

    degree = None
    field = None

    if academic_text:

        degree, field = (
            _parse_degree_field(
                academic_text
            )
        )

    # -----------------------------------------------------
    # If degree was not found in academic text,
    # try complete original text.
    # -----------------------------------------------------

    if not degree:

        complete_text = _clean_field(
            " ".join(lines)
        )

        degree, field = (
            _parse_degree_field(
                complete_text
            )
        )

    # -----------------------------------------------------
    # If no recognizable degree, preserve academic text
    # as field.
    # -----------------------------------------------------

    if not degree and academic_text:

        field = academic_text

    # -----------------------------------------------------
    # Clean field
    # -----------------------------------------------------

    if field:

        field = _remove_non_core_text(
            field
        )

        if institution:

            field = re.sub(
                re.escape(institution),
                "",
                field,
                flags=re.IGNORECASE,
            )

        field = re.sub(
            r"\bat\s+.+$",
            "",
            field,
            flags=re.IGNORECASE,
        )

        field = re.sub(
            r"^(?:Indien|India|Deutschland|Germany)"
            r"\s+",
            "",
            field,
            flags=re.IGNORECASE,
        )

        field = _clean_field(
            field
        )

    # -----------------------------------------------------
    # Do not create meaningless records.
    # -----------------------------------------------------

    if not institution and not degree and not field:
        return None

    return {
        "institution": institution,
        "degree": degree,
        "field_of_study": field,
        "grade": grade,
        "start_date": start_date,
        "end_date": end_date,
    }


# =========================================================
# Entry detection
# =========================================================

def _is_strong_academic_line(line):

    if not line:
        return False

    lower = line.lower()

    if _looks_like_institution(line):
        return True

    if _is_degree_line(line):
        return True

    if "mechanical engineering" in lower:
        return True

    if "robotic systems engineering" in lower:
        return True

    if "computer science" in lower:
        return True

    if "engineering" in lower:
        return True

    if "science" in lower:
        return True

    if "abitur" in lower:
        return True

    return False


def _find_entry_starts(lines):

    starts = []

    for index, line in enumerate(lines):

        if _is_degree_line(line):

            starts.append(index)
            continue

        if _looks_like_institution(line):

            starts.append(index)
            continue

        if re.search(
            r"\b("
            r"bachelor"
            r"|master"
            r"|b\.eng"
            r"|m\.eng"
            r"|b\.sc"
            r"|m\.sc"
            r"|diplom"
            r"|abitur"
            r")\b",
            line,
            re.IGNORECASE,
        ):

            starts.append(index)

    return starts


# =========================================================
# Date near entry
# =========================================================

def _find_date_near_entry(
    lines,
    start,
    end,
):

    for index in range(
        start,
        end,
    ):

        line = lines[index]

        start_date, end_date = (
            _extract_dates(line)
        )

        if start_date is not None or end_date is not None:

            return (
                start_date,
                end_date,
            )

    return None, None


# =========================================================
# Main extraction
# =========================================================

def extract_education(section_text):

    if not section_text:
        return []

    lines = _normalize_lines(
        section_text
    )

    if not lines:
        return []

    starts = _find_entry_starts(lines)

    if not starts:
        return []

    # Remove adjacent starts belonging to same entry.
    filtered_starts = []

    for index in starts:

        if not filtered_starts:

            filtered_starts.append(index)
            continue

        previous = filtered_starts[-1]

        if index - previous <= 1:
            continue

        filtered_starts.append(index)

    starts = filtered_starts

    candidates = []

    # -----------------------------------------------------
    # Build blocks.
    # -----------------------------------------------------

    for n, start_index in enumerate(starts):

        next_start = (
            starts[n + 1]
            if n + 1 < len(starts)
            else len(lines)
        )

        block_end = min(
            next_start,
            start_index + 8,
        )

        block = lines[
            start_index:block_end
        ]

        start_date, end_date = (
            _find_date_near_entry(
                block,
                0,
                len(block),
            )
        )

        if start_date is None and end_date is None:
            continue

        candidate = _build_candidate(
            block,
            start_date,
            end_date,
        )

        if candidate:
            candidates.append(candidate)

    # =====================================================
    # Deduplicate
    # =====================================================

    education = []
    seen = set()

    for item in candidates:

        key = (
            item.get("institution"),
            item.get("degree"),
            item.get("field_of_study"),
            item.get("grade"),
            item.get("start_date"),
            item.get("end_date"),
        )

        if key in seen:
            continue

        seen.add(key)
        education.append(item)

    # =====================================================
    # Merge compatible records only.
    # =====================================================

    merged = []

    for item in education:

        merged_into_existing = False

        for existing in merged:

            same_dates = (
                existing["start_date"]
                == item["start_date"]
                and
                existing["end_date"]
                == item["end_date"]
            )

            same_degree = (
                existing["degree"]
                == item["degree"]
                or
                not existing["degree"]
                or
                not item["degree"]
            )

            same_institution = (
                existing["institution"]
                == item["institution"]
                or
                not existing["institution"]
                or
                not item["institution"]
            )

            if not (
                same_dates
                and same_degree
                and same_institution
            ):
                continue

            if (
                not existing["institution"]
                and item["institution"]
            ):
                existing["institution"] = (
                    item["institution"]
                )

            if (
                not existing["degree"]
                and item["degree"]
            ):
                existing["degree"] = (
                    item["degree"]
                )

            if (
                not existing["field_of_study"]
                and item["field_of_study"]
            ):
                existing["field_of_study"] = (
                    item["field_of_study"]
                )

            if (
                not existing["grade"]
                and item["grade"]
            ):
                existing["grade"] = (
                    item["grade"]
                )

            merged_into_existing = True
            break

        if not merged_into_existing:
            merged.append(item)

    # =====================================================
    # Sort chronologically.
    # =====================================================

    merged.sort(
        key=lambda item: (
            item["start_date"]
            or "9999-99"
        )
    )

    return merged