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
# Date parsing
# =========================================================

def parse_date(value):
    """
    Convert common CV date formats to YYYY-MM.

    Examples:
        10/2024
        2024-10
        October 2024
        Oktober 2024
        2024

    A standalone year is normalized to January.
    """

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


def _extract_dates(line):
    """
    Extract start/end dates from a line.
    """

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
        r"^[\uf0b7\u2022\u25cf\u25aaò§P]+\s*",
        "",
        line,
    )

    # Broken dash encoding
    line = line.replace("û", "–")

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

    # Note: 2.1
    re.compile(
        r"\bNote\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    # Grade: 2.1
    re.compile(
        r"\bGrade\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    # GPA: 3.8
    re.compile(
        r"\bGPA\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    # CGPA: 8.4
    re.compile(
        r"\bCGPA\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    # Gesamtnote: 2.1
    re.compile(
        r"\bGesamtnote\s*[:\-]?\s*"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"(?:\s*/\s*[0-9]+)?)",
        re.IGNORECASE,
    ),

    # 8.4/10
    re.compile(
        r"\b"
        r"([0-9]+(?:[.,][0-9]+)?"
        r"\s*/\s*[0-9]+)"
        r"\b",
        re.IGNORECASE,
    ),

    # 97.75%
    re.compile(
        r"\b"
        r"([0-9]+(?:[.,][0-9]+)?\s*%)"
        r"\b",
        re.IGNORECASE,
    ),
]


def _extract_grade(lines):
    """
    Extract the first educational grade/GPA.

    Returns:
        grade, cleaned_lines
    """

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
    "hochschule",
    "rwth",
    "school",
    "schule",
    "gymnasium",
    "college",
    "institute",
    "institut",
    "university of",
    "universidade",
)


def _looks_like_institution(line):
    if not line:
        return False

    lower = line.lower()

    return any(
        indicator in lower
        for indicator in INSTITUTION_INDICATORS
    )


def _extract_institution(lines):
    """
    Find the strongest institution-looking line.
    """

    for line in lines:

        if _looks_like_institution(line):

            return _clean_field(line)

    return None


# =========================================================
# Degree detection
# =========================================================

DEGREE_PATTERNS = [

    # B.Sc / M.Sc / B.Eng / M.Eng
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

    # Bachelor / Master
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
    if not value:
        return None

    value = value.strip()

    normalized = re.sub(
        r"[\s.]",
        "",
        value.lower(),
    )

    mapping = {

        "bsc":
            "B.Sc",

        "msc":
            "M.Sc",

        "beng":
            "B.Eng",

        "meng":
            "M.Eng",

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
    """
    Parse degree and field from one academic text block.

    Supported examples:

        Master of Science, RWTH Aachen
        Master of Science in Robotics
        Bachelor of Engineering in Mechanical Engineering
        Mechanical Engineering B.Eng.
        Computational Engineering Science B.Sc.
        Robotic Systems Engineering M.Sc.
        Abitur
    """

    if not text:
        return None, None

    text = _clean_field(text)

    # -----------------------------------------------------
    # Remove institution after "at"
    # -----------------------------------------------------

    text_without_institution = re.sub(
        r"\s+\bat\s+.+$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text_without_institution = _clean_field(
        text_without_institution
    )

    # -----------------------------------------------------
    # Abitur
    # -----------------------------------------------------

    if re.search(
        r"\bAbitur\b",
        text,
        re.IGNORECASE,
    ):
        return "Abitur", None

    # -----------------------------------------------------
    # Full Bachelor/Master ... in FIELD
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Find degree abbreviation/full degree
    # -----------------------------------------------------

    degree_match = None

    # Longest patterns first
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

    # -----------------------------------------------------
    # Determine field.
    #
    # Mechanical Engineering B.Eng.
    # -> field = Mechanical Engineering
    #
    # B.Eng. Mechanical Engineering
    # -> field = Mechanical Engineering
    # -----------------------------------------------------

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
    """
    Split common forms:

        Degree at RWTH Aachen University

    and:

        Degree, RWTH Aachen University
    """

    if not text:
        return text, None

    # -----------------------------------------------------
    # "at UNIVERSITY"
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # ", UNIVERSITY"
    #
    # Be conservative: only split if the right side
    # actually looks like an institution.
    # -----------------------------------------------------

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
    "wahlfach",
    "electives",
    "elective courses",
    "expected graduation",
    "expected completion",
    "voraussichtlicher abschluss",
    "voraussichtlicher",
    "coursework",
)


def _is_non_core_line(line):
    if not line:
        return False

    lower = line.lower()

    return any(
        pattern in lower
        for pattern in NON_CORE_PATTERNS
    )


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

    # Remove obvious academic degree prefix.
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
    """
    Build one education record from a local group
    of education lines.
    """

    if not lines:
        return None

    # Remove date lines.
    lines = [
        line
        for line in lines
        if not _is_date_line(line)
    ]

    # Remove supplementary/course lines.
    lines = [
        line
        for line in lines
        if not _is_non_core_line(line)
    ]

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
    # try the complete original text.
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
    # If there is institution + remaining text but no
    # recognizable degree, preserve remaining text as field.
    # -----------------------------------------------------

    if not degree and academic_text:

        field = academic_text

    # -----------------------------------------------------
    # Clean field
    # -----------------------------------------------------

    if field and institution:

        # Remove institution if it leaked into field.
        field = re.sub(
            re.escape(institution),
            "",
            field,
            flags=re.IGNORECASE,
        )

        field = _clean_field(
            field
        )

    # Remove common institution leftovers.
    if field:

        field = re.sub(
            r"\bat\s+.+$",
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
# Entry grouping
# =========================================================

def _find_date_positions(lines):
    """
    Return all education date positions.
    """

    positions = []

    for index, line in enumerate(lines):

        start, end = _extract_dates(
            line
        )

        if start is not None or end is not None:

            positions.append(
                (
                    index,
                    start,
                    end,
                )
            )

    return positions


def _is_strong_academic_line(line):
    """
    Determine whether a line is strongly associated with
    education.
    """

    if not line:
        return False

    lower = line.lower()

    if _looks_like_institution(line):
        return True

    if any(
        pattern.search(line)
        for pattern in DEGREE_PATTERNS
    ):
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


# =========================================================
# Main extraction
# =========================================================

def extract_education(section_text):
    """
    Extract education records from an EDUCATION section.

    Designed for CVs where entries may appear as:

        Degree
        Institution
        Date

    or:

        Institution
        Degree
        Date

    or:

        Date
        Degree
        Institution

    or:

        Degree at Institution
        Date

    or:

        Degree, Institution
        Date

    The extractor deliberately uses local context around
    dates instead of treating every line independently.
    """

    if not section_text:
        return []

    lines = _normalize_lines(
        section_text
    )

    if not lines:
        return []

    date_positions = _find_date_positions(
        lines
    )

    if not date_positions:
        return []

    candidates = []

    # =====================================================
    # Build one candidate around each date.
    # =====================================================

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
        # Lines surrounding this date.
        # -------------------------------------------------

        before = lines[
            previous_date_index + 1:
            date_index
        ]

        after = lines[
            date_index + 1:
            next_date_index
        ]

        # -------------------------------------------------
        # Remove unrelated date lines.
        # -------------------------------------------------

        before = [
            line
            for line in before
            if not _is_date_line(line)
        ]

        after = [
            line
            for line in after
            if not _is_date_line(line)
        ]

        # -------------------------------------------------
        # Limit context.
        #
        # Education entries are normally only a few lines.
        # We avoid swallowing an entire section.
        # -------------------------------------------------

        before_context = before[-5:]
        after_context = after[:5]

        # -------------------------------------------------
        # Score each side.
        # -------------------------------------------------

        def score(lineset):

            if not lineset:
                return -100

            score_value = 0

            for line in lineset:

                if _looks_like_institution(line):
                    score_value += 5

                if any(
                    pattern.search(line)
                    for pattern in DEGREE_PATTERNS
                ):
                    score_value += 5

                if _is_strong_academic_line(line):
                    score_value += 2

                if re.search(
                    r"\b(?:Note|Grade|GPA|CGPA|Gesamtnote)\b",
                    line,
                    re.IGNORECASE,
                ):
                    score_value += 2

            return score_value

        before_score = score(
            before_context
        )

        after_score = score(
            after_context
        )

        # -------------------------------------------------
        # Choose best context.
        # -------------------------------------------------

        if before_score > after_score:

            content = before_context

        elif after_score > before_score:

            content = after_context

        else:

            # If both sides are useful, combine them.
            content = (
                before_context +
                after_context
            )

        candidate = _build_candidate(
            content,
            start_date,
            end_date,
        )

        if candidate:

            candidates.append(
                candidate
            )

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
    # Remove obviously duplicated/fragmented entries.
    #
    # Example:
    #   Master of Science, RWTH Aachen
    #
    # and:
    #   Robotic Systems Engineering
    #
    # should become one entry when they share dates.
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

            if not same_dates:
                continue

            # -------------------------------------------------
            # Merge missing institution.
            # -------------------------------------------------

            if (
                not existing["institution"]
                and item["institution"]
            ):
                existing["institution"] = (
                    item["institution"]
                )

            # -------------------------------------------------
            # Merge missing degree.
            # -------------------------------------------------

            if (
                not existing["degree"]
                and item["degree"]
            ):
                existing["degree"] = (
                    item["degree"]
                )

            # -------------------------------------------------
            # Merge missing field.
            # -------------------------------------------------

            if (
                not existing["field_of_study"]
                and item["field_of_study"]
            ):
                existing["field_of_study"] = (
                    item["field_of_study"]
                )

            # -------------------------------------------------
            # Merge grade.
            # -------------------------------------------------

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