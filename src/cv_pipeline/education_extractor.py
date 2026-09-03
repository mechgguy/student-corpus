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


def parse_date(value):
    """
    Convert common CV date formats to YYYY-MM.

    Examples:
        10/2024
        2024-10
        October 2024
        Oktober 2024
        2024

    Open-ended values such as Present / Since / seit are
    handled by the caller and return None here.
    """

    if not value:
        return None

    value = value.strip()
    value = value.rstrip(":;,.")

    # MM/YYYY
    match = re.fullmatch(r"(\d{1,2})[/-](\d{4})", value)

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}"

    # YYYY/MM or YYYY-MM
    match = re.fullmatch(r"(\d{4})[/-](\d{1,2})", value)

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
        r"([A-Za-zÄÖÜäöüß]+)\s+(\d{4})",
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


# =========================================================
# Date patterns
# =========================================================

DATE_TOKEN = r"""
(?:
    \d{1,2}[/-]\d{4}
    |
    \d{4}[/-]\d{1,2}
    |
    \d{4}
    |
    [A-Za-zÄÖÜäöüß]+\s+\d{4}
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
        û
        |
        to
        |
        bis
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
# Cleaning
# =========================================================

def _clean_line(line):
    """
    Clean common PDF extraction artifacts.
    """

    if not line:
        return ""

    line = line.strip()

    # PDF bullet artifacts.
    line = re.sub(
        r"^[\uf0b7\u2022\u25cf\u25aaò]+\s*",
        "",
        line,
    )

    # Broken dash encoding.
    line = line.replace("û", "–")

    # Excessive whitespace.
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def _clean_field(value):
    """
    Clean an extracted field.
    """

    if not value:
        return None

    value = value.strip()

    # Leading punctuation.
    value = re.sub(
        r"^[\s:;,.–—-]+",
        "",
        value,
    )

    # Trailing punctuation.
    value = re.sub(
        r"[\s:;,.]+$",
        "",
        value,
    )

    # Remove accidental duplicate whitespace.
    value = re.sub(r"\s+", " ", value)

    return value.strip() or None


def _normalize_lines(text):
    """
    Convert section text to clean lines.
    """

    if not text:
        return []

    lines = []

    for line in text.splitlines():

        line = _clean_line(line)

        if line:
            lines.append(line)

    return lines


# =========================================================
# Date extraction
# =========================================================

def _extract_dates(line):
    """
    Extract start/end dates from a line.

    Returns:
        (start_date, end_date)

    Examples:

        10/2024 - 09/2026
            -> ("2024-10", "2026-09")

        10/2024 - Present
            -> ("2024-10", None)

        seit 10/2022
            -> ("2022-10", None)
    """

    match = DATE_RANGE_PATTERN.search(line)

    if match:

        start = parse_date(match.group("start"))

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
        start = parse_date(match.group("date"))
        return start, None

    return None, None


def _is_date_line(line):
    """
    True if the line primarily contains date information.
    """

    start, end = _extract_dates(line)

    if start is not None or end is not None:
        return True

    return False


# =========================================================
# Grade extraction
# =========================================================

GRADE_PATTERNS = [
    re.compile(
        r"\bGPA\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bCGPA\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bGrade\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bNote\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bGesamtnote\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?)",
        re.IGNORECASE,
    ),
]


def _extract_grade(lines):
    """
    Extract GPA / grade from the entry.

    Returns:
        grade, cleaned_lines
    """

    grade = None
    cleaned_lines = []

    for line in lines:

        current = line

        for pattern in GRADE_PATTERNS:

            match = pattern.search(current)

            if match:

                grade = match.group(1).replace(",", ".")

                current = pattern.sub("", current)

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
    "hochschule",
    "rwth",
    "school",
    "schule",
    "gymnasium",
    "college",
    "institute",
    "institut",
)


def _looks_like_institution(line):
    """
    Determine whether a line looks like an educational institution.
    """

    lower = line.lower()

    return any(
        indicator in lower
        for indicator in INSTITUTION_INDICATORS
    )


def _extract_institution(lines):
    """
    Extract institution from lines.
    """

    for line in lines:

        if _looks_like_institution(line):

            institution = line

            # Remove trailing punctuation.
            institution = _clean_field(institution)

            return institution

    return None


# =========================================================
# Degree detection
# =========================================================

DEGREE_PATTERNS = [
    # B.Sc / M.Sc
    re.compile(
        r"\bB\.?\s*Sc\.?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bM\.?\s*Sc\.?\b",
        re.IGNORECASE,
    ),

    # B.Eng / M.Eng
    re.compile(
        r"\bB\.?\s*Eng\.?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bM\.?\s*Eng\.?\b",
        re.IGNORECASE,
    ),

    # Bachelor / Master
    re.compile(
        r"\bBachelor(?:\s+of)?(?:\s+Engineering)?\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bMaster(?:\s+of)?(?:\s+Engineering)?\b",
        re.IGNORECASE,
    ),

    # German
    re.compile(
        r"\bDiplom\b",
        re.IGNORECASE,
    ),

    re.compile(
        r"\bAbitur\b",
        re.IGNORECASE,
    ),
]


def _normalize_degree(value):
    """
    Normalize common degree abbreviations.
    """

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
    }

    return mapping.get(
        normalized,
        _clean_field(value),
    )


# =========================================================
# Degree + field parsing
# =========================================================

def _parse_degree_field(text):
    """
    Extract degree and field from a text block.

    Handles:

        M.Sc. Nachhaltige Energieversorgung

        Computational Engineering Science B.Sc.

        Bachelor of Engineering in Mechanical Engineering

        M.Sc. Computational Engineering Science
    """

    if not text:
        return None, None

    text = _clean_field(text)

    # -----------------------------------------------------
    # Bachelor/Master ... in FIELD
    # -----------------------------------------------------

    match = re.search(
        r"\b("
        r" Bachelor\s+of\s+Engineering"
        r"|Bachelor\s+of\s+Science"
        r"|Bachelor"
        r"|Master\s+of\s+Engineering"
        r"|Master\s+of\s+Science"
        r"|Master"
        r")"
        r"\s+in\s+(.+)",
        text,
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

    # -----------------------------------------------------
    # Abitur
    # -----------------------------------------------------

    match = re.search(
        r"\bAbitur\b",
        text,
        re.IGNORECASE,
    )

    if match:

        return "Abitur", None

    # -----------------------------------------------------
    # B.Sc / M.Sc / B.Eng / M.Eng
    # -----------------------------------------------------

    degree_match = None

    for pattern in DEGREE_PATTERNS:

        match = pattern.search(text)

        if match:

            degree_match = match

            break

    if not degree_match:
        return None, None

    degree = _normalize_degree(
        degree_match.group(0)
    )

    before = text[:degree_match.start()].strip()
    after = text[degree_match.end():].strip()

    # -----------------------------------------------------
    # Determine field.
    #
    # Example:
    # Computational Engineering Science B.Sc.
    #
    # before = Computational Engineering Science
    # after  = ""
    # -----------------------------------------------------

    if before:

        field = before

    elif after:

        field = after

    else:

        field = None

    # Remove "at UNIVERSITY" from field.
    if field:

        field = re.sub(
            r"\bat\s+.+$",
            "",
            field,
            flags=re.IGNORECASE,
        )

        field = re.sub(
            r"\ban\s+der\s+.+$",
            "",
            field,
            flags=re.IGNORECASE,
        )

    field = _clean_field(field)

    return degree, field


# =========================================================
# Split institution from degree line
# =========================================================

def _split_at_institution(text):
    """
    Split:

        Computational Engineering Science B.Sc. at RWTH Aachen University

    into:

        academic_part
        institution
    """

    if not text:
        return text, None

    match = re.search(
        r"\s+\bat\s+(.+)$",
        text,
        re.IGNORECASE,
    )

    if match:

        academic_part = text[:match.start()]
        institution = match.group(1)

        return (
            _clean_field(academic_part),
            _clean_field(institution),
        )

    return text, None


# =========================================================
# Relevant-course filtering
# =========================================================

NON_CORE_PATTERNS = (
    "relevant courses",
    "relevant modules",
    "schwerpunkte",
    "fachrichtungen",
    "expected graduation",
    "expected completion",
    "voraussichtlicher abschluss",
    "voraussichtlicher",
)


def _is_non_core_line(line):
    lower = line.lower()

    return any(
        pattern in lower
        for pattern in NON_CORE_PATTERNS
    )


def _remove_non_core_lines(lines):
    """
    Prevent course lists and supplementary information
    from becoming degree/field/institution.
    """

    result = []

    for line in lines:

        if _is_non_core_line(line):
            continue

        result.append(line)

    return result


# =========================================================
# Candidate entry construction
# =========================================================

def _build_candidate(
    lines,
    start_date,
    end_date,
):
    """
    Convert a group of lines into one education record.
    """

    if not lines:
        return None

    lines = _remove_non_core_lines(lines)

    if not lines:
        return None

    grade, lines = _extract_grade(lines)

    if not lines:
        return None

    # -----------------------------------------------------
    # First find explicit "at UNIVERSITY".
    # -----------------------------------------------------

    institution = None
    academic_lines = []

    for line in lines:

        academic_part, explicit_institution = (
            _split_at_institution(line)
        )

        if explicit_institution:

            institution = explicit_institution

            if academic_part:
                academic_lines.append(academic_part)

        else:

            academic_lines.append(line)

    # -----------------------------------------------------
    # Otherwise identify institution from a separate line.
    # -----------------------------------------------------

    if not institution:

        institution = _extract_institution(
            academic_lines
        )

        if institution:

            academic_lines = [
                line
                for line in academic_lines
                if line != institution
            ]

    # -----------------------------------------------------
    # Join academic information.
    # -----------------------------------------------------

    academic_text = " ".join(
        academic_lines
    )

    academic_text = _clean_field(
        academic_text
    )

    degree, field = _parse_degree_field(
        academic_text
    )

    # -----------------------------------------------------
    # If no degree was detected, we can still have a field
    # or school education.
    # -----------------------------------------------------

    if not degree and academic_text:

        # If institution already identified, remaining
        # academic text can represent a field/title.
        field = _clean_field(
            academic_text
        )

    # -----------------------------------------------------
    # Clean institution.
    # -----------------------------------------------------

    institution = _clean_field(
        institution
    )

    # -----------------------------------------------------
    # Avoid putting institution into field.
    # -----------------------------------------------------

    if field and institution:

        field = field.replace(
            institution,
            "",
        )

        field = _clean_field(field)

    # -----------------------------------------------------
    # Remove "at UNIVERSITY" leftovers.
    # -----------------------------------------------------

    if field:

        field = re.sub(
            r"\bat\s+.*$",
            "",
            field,
            flags=re.IGNORECASE,
        )

        field = _clean_field(field)

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
# Main extraction
# =========================================================

def extract_education(section_text):
    """
    Extract education from an EDUCATION section.

    Designed for English and German CVs with varying layouts.

    Supported layouts include:

        Degree
        Institution
        Date

    and:

        Date
        Degree
        Institution

    and:

        Degree at Institution
        Date

    and:

        Date
        Institution
        Degree
    """

    if not section_text:
        return []

    lines = _normalize_lines(
        section_text
    )

    if not lines:
        return []

    # -----------------------------------------------------
    # Find date lines.
    # -----------------------------------------------------

    date_positions = []

    for index, line in enumerate(lines):

        start, end = _extract_dates(line)

        if start is not None or end is not None:

            date_positions.append(
                (
                    index,
                    start,
                    end,
                )
            )

    if not date_positions:
        return []

    candidates = []

    # -----------------------------------------------------
    # Process each date.
    # -----------------------------------------------------

    for n, (
        date_index,
        start_date,
        end_date,
    ) in enumerate(date_positions):

        previous_date_index = (
            date_positions[n - 1][0]
            if n > 0
            else -1
        )

        next_date_index = (
            date_positions[n + 1][0]
            if n + 1 < len(date_positions)
            else len(lines)
        )

        # -------------------------------------------------
        # Information after date.
        #
        # Example:
        #
        # 10/2025 - Present
        # RWTH Aachen University
        # MSc ...
        # -------------------------------------------------

        after_lines = lines[
            date_index + 1:
            next_date_index
        ]

        # -------------------------------------------------
        # Information before date.
        #
        # Example:
        #
        # MSc ...
        # RWTH Aachen University
        # 10/2025 - Present
        # -------------------------------------------------

        before_lines = lines[
            previous_date_index + 1:
            date_index
        ]

        # Remove unrelated date lines.
        before_lines = [
            line
            for line in before_lines
            if not _is_date_line(line)
        ]

        after_lines = [
            line
            for line in after_lines
            if not _is_date_line(line)
        ]

        # -------------------------------------------------
        # Prefer the side containing degree/institution.
        # -------------------------------------------------

        def score(lineset):

            if not lineset:
                return -1

            text = " ".join(lineset).lower()

            score_value = 0

            if any(
                _looks_like_institution(line)
                for line in lineset
            ):
                score_value += 5

            if any(
                pattern.search(text)
                for pattern in DEGREE_PATTERNS
            ):
                score_value += 5

            if " at " in text:
                score_value += 2

            if " in " in text:
                score_value += 1

            return score_value

        before_score = score(
            before_lines
        )

        after_score = score(
            after_lines
        )

        if after_score > before_score:

            content = after_lines

        elif before_score > after_score:

            content = before_lines

        else:

            # If both are equally useful, prefer after.
            content = (
                after_lines
                if after_lines
                else before_lines
            )

        candidate = _build_candidate(
            content,
            start_date,
            end_date,
        )

        if candidate:
            candidates.append(candidate)

    # -----------------------------------------------------
    # Remove duplicates.
    # -----------------------------------------------------

    education = []

    seen = set()

    for item in candidates:

        key = (
            item["institution"],
            item["degree"],
            item["field_of_study"],
            item["start_date"],
            item["end_date"],
        )

        if key in seen:
            continue

        seen.add(key)

        education.append(item)

    # -----------------------------------------------------
    # Sort chronologically.
    # -----------------------------------------------------

    education.sort(
        key=lambda x: (
            x["start_date"] or "9999-99"
        )
    )

    return education
