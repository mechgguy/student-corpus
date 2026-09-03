import re
from datetime import datetime


# =========================================================
# Configuration
# =========================================================

MONTHS = {
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
}


STOP_SECTIONS = {
    # English
    "social engagement",
    "social involvement",
    "volunteer experience",
    "volunteering",
    "extracurricular activities",

    # German
    "ehrenamt",
    "ehrenamtliche tätigkeiten",
    "soziales engagement",
    "soziales engagement",
    "freiwilligenarbeit",
}


# =========================================================
# Text normalization
# =========================================================

def _clean_line(line):
    """
    Normalize common PDF extraction artifacts.

    This is intentionally conservative.
    """

    if not line:
        return ""

    line = line.strip()

    # Common bullet characters / OCR artifacts
    line = re.sub(r"^[\uf0b7\u2022\u25aa\u25cfò]+\s*", "", line)

    # Normalize common dash variants.
    line = line.replace("–", "-")
    line = line.replace("—", "-")
    line = line.replace("-", "-")
    line = line.replace("û", "-")

    # Collapse whitespace.
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def _clean_text(text):
    """
    Convert extracted PDF text into meaningful lines.
    """

    lines = []

    for raw_line in text.splitlines():

        line = _clean_line(raw_line)

        if line:
            lines.append(line)

    return lines


# =========================================================
# Section detection
# =========================================================

def _normalize_section_name(line):
    line = line.lower()
    line = re.sub(r"[^a-zäöüß ]", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def _looks_like_stop_section(line):
    normalized = _normalize_section_name(line)
    return normalized in STOP_SECTIONS


# =========================================================
# Date parsing
# =========================================================

PRESENT_PATTERN = re.compile(
    r"^(present|current|ongoing|now|heute)$",
    re.IGNORECASE,
)


def parse_date(value):
    """
    Convert common CV date formats to YYYY-MM.

    Supported examples:

        08/2023
        2023/08
        2023-08
        2023
        January 2025
        Jan 2025
        Present
        Current
    """

    if not value:
        return None

    value = value.strip()

    # Present / current
    if PRESENT_PATTERN.fullmatch(value):
        return datetime.now().strftime("%Y-%m")

    # MM/YYYY or MM-YYYY
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
        r"([A-Za-z]+)\s+(\d{4})",
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
# Date detection
# =========================================================

DATE_TOKEN = (
    r"(?:"
    r"\d{1,2}[/-]\d{4}"
    r"|"
    r"\d{4}[/-]\d{1,2}"
    r"|"
    r"\d{4}"
    r"|"
    r"[A-Za-z]+\s+\d{4}"
    r"|"
    r"Present"
    r"|"
    r"Current"
    r"|"
    r"Ongoing"
    r"|"
    r"Now"
    r")"
)


DATE_RANGE_PATTERN = re.compile(
    rf"""
    (?P<start>{DATE_TOKEN})
    \s*
    (?:-|to)
    \s*
    (?P<end>{DATE_TOKEN})
    """,
    re.IGNORECASE | re.VERBOSE,
)


SINGLE_DATE_PATTERN = re.compile(
    rf"^\s*(?P<date>{DATE_TOKEN})\s*$",
    re.IGNORECASE,
)


def find_date_range(line):
    """
    Find a date range anywhere in a line.
    """

    match = DATE_RANGE_PATTERN.search(line)

    if not match:
        return None

    start = parse_date(match.group("start"))
    end = parse_date(match.group("end"))

    if not start or not end:
        return None

    return {
        "start": start,
        "end": end,
        "start_pos": match.start(),
        "end_pos": match.end(),
    }


def find_single_date(line):
    """
    Detect a line containing only a single year/date.

    Example:

        2020
    """

    match = SINGLE_DATE_PATTERN.match(line)

    if not match:
        return None

    date = parse_date(match.group("date"))

    if not date:
        return None

    return {
        "start": date,
        "end": date,
    }


# =========================================================
# Duration
# =========================================================

def calculate_duration(start_date, end_date):

    if not start_date or not end_date:
        return None

    try:
        start = datetime.strptime(start_date, "%Y-%m")
        end = datetime.strptime(end_date, "%Y-%m")
    except ValueError:
        return None

    months = (
        (end.year - start.year) * 12
        + (end.month - start.month)
    )

    if months < 0:
        return None

    return round(months / 12, 2)


# =========================================================
# Entry classification
# =========================================================

def _is_bullet(line):
    return bool(
        re.match(
            r"^[\uf0b7\u2022\u25aa\u25cfò]",
            line,
        )
    )


def _looks_like_location(line):
    """
    Conservative location detection.

    Examples:

        Pune, India
        Ingolstadt
        Cologne
        China
    """

    if not line:
        return False

    # Strong signal: comma-separated location
    if "," in line and len(line.split()) <= 8:
        return True

    # Country-only locations
    countries = {
        "china",
        "india",
        "germany",
        "france",
        "uk",
        "usa",
        "united states",
        "united kingdom",
    }

    if line.lower() in countries:
        return True

    return False


def _looks_like_description(line):
    """
    Detect obvious description/bullet lines.
    """

    if _is_bullet(line):
        return True

    description_words = (
        "responsible",
        "responsibilities",
        "managed",
        "developed",
        "designed",
        "implemented",
        "performed",
        "supported",
        "worked",
        "oversaw",
        "conducted",
        "durchführung",
        "durchführung",
        "unterstützung",
        "erstellung",
        "mitarbeit",
        "entwicklung",
    )

    lower = line.lower()

    return any(
        lower.startswith(word)
        for word in description_words
    )


def _extract_company_from_title(title):
    """
    Handle:

        Working Student at TWT GmbH
        Internship at Audi AG

    """

    match = re.search(
        r"\bat\s+(.+)$",
        title,
        re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1).strip()


# =========================================================
# Entry parsing
# =========================================================

def _parse_entry(block, date_info, date_index):
    """
    Parse one candidate experience block.

    The date may occur either:

        DATE
        TITLE
        COMPANY
        LOCATION

    or:

        TITLE
        COMPANY
        DATE
        LOCATION

    or:

        TITLE
        DATE
        COMPANY
    """

    if not block:
        return None

    lines = [
        line
        for line in block
        if line
    ]

    if not lines:
        return None

    # -----------------------------------------------------
    # Remove date line itself
    # -----------------------------------------------------

    content = []

    for i, line in enumerate(lines):

        if i == date_index:
            continue

        # Remove date from lines containing inline ranges.
        cleaned = DATE_RANGE_PATTERN.sub("", line).strip()

        if cleaned:
            content.append(cleaned)

    if not content:
        return None

    # -----------------------------------------------------
    # Separate description
    # -----------------------------------------------------

    metadata = []
    description = []

    for line in content:

        if _looks_like_description(line):
            description.append(line)
        else:
            metadata.append(line)

    # -----------------------------------------------------
    # Position
    # -----------------------------------------------------

    position = None
    company = None
    location = None

    if metadata:

        first = metadata[0]

        # "Working Student at TWT GmbH"
        at_company = _extract_company_from_title(first)

        if at_company:
            position = first
            company = at_company

        else:
            position = first

    # -----------------------------------------------------
    # Remaining metadata
    # -----------------------------------------------------

    remaining = metadata[1:]

    for line in remaining:

        if not company and _looks_like_location(line):
            location = line
            continue

        if not company:
            company = line
            continue

        if not location and _looks_like_location(line):
            location = line

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    if not description:

        # Anything left after metadata classification can
        # become description later if needed.
        description_text = None

    else:
        description_text = " ".join(description)

    # -----------------------------------------------------
    # Validate
    # -----------------------------------------------------

    if not position:
        return None

    duration = calculate_duration(
        date_info["start"],
        date_info["end"],
    )

    return {
        "position": position,
        "company": company,
        "location": location,
        "start_date": date_info["start"],
        "end_date": date_info["end"],
        "description": description_text,
        "duration_years": duration,
    }


# =========================================================
# Experience extraction
# =========================================================

def extract_experience(section_text):

    if not section_text:
        return []

    lines = _clean_text(section_text)

    if not lines:
        return []

    # -----------------------------------------------------
    # Find all date anchors
    # -----------------------------------------------------

    date_anchors = []

    for i, line in enumerate(lines):

        range_info = find_date_range(line)

        if range_info:
            date_anchors.append(
                {
                    "index": i,
                    "start": range_info["start"],
                    "end": range_info["end"],
                    "type": "range",
                }
            )
            continue

        single_info = find_single_date(line)

        if single_info:
            date_anchors.append(
                {
                    "index": i,
                    "start": single_info["start"],
                    "end": single_info["end"],
                    "type": "single",
                }
            )

    if not date_anchors:
        return []

    experiences = []

    # -----------------------------------------------------
    # Process date anchors
    # -----------------------------------------------------

    for anchor_index, anchor in enumerate(date_anchors):

        date_index = anchor["index"]

        # Stop at social/volunteer sections.
        before = lines[:date_index]

        if before:
            recent_section = before[-1]

            if _looks_like_stop_section(recent_section):
                continue

        # -------------------------------------------------
        # Determine surrounding block
        # -------------------------------------------------

        next_date_index = (
            date_anchors[anchor_index + 1]["index"]
            if anchor_index + 1 < len(date_anchors)
            else len(lines)
        )

        previous_date_index = (
            date_anchors[anchor_index - 1]["index"]
            if anchor_index > 0
            else -1
        )

        # -------------------------------------------------
        # Layout A:
        #
        # DATE
        # TITLE
        # COMPANY
        # LOCATION
        #
        # Use text after date.
        # -------------------------------------------------

        after_block = lines[
            date_index:next_date_index
        ]

        after_content = after_block[1:]

        if after_content:

            first = after_content[0]

            # Strong indication that this is a title.
            if (
                not _looks_like_location(first)
                and not _looks_like_description(first)
            ):

                block = after_block

                result = _parse_entry(
                    block,
                    anchor,
                    0,
                )

                if result:
                    experiences.append(result)

                    continue

        # -------------------------------------------------
        # Layout B:
        #
        # TITLE
        # COMPANY
        # DATE
        # LOCATION
        #
        # Use text before date.
        # -------------------------------------------------

        before_block = lines[
            previous_date_index + 1:date_index + 1
        ]

        if len(before_block) > 1:

            result = _parse_entry(
                before_block,
                anchor,
                len(before_block) - 1,
            )

            if result:
                experiences.append(result)

                # Add immediate location after date.
                if next_date_index > date_index + 1:

                    possible_location = lines[
                        date_index + 1
                    ]

                    if _looks_like_location(
                        possible_location
                    ):
                        result["location"] = (
                            possible_location
                        )

                continue

    return _remove_duplicate_experiences(experiences)


# =========================================================
# Duplicate protection
# =========================================================

def _remove_duplicate_experiences(experiences):

    unique = []
    seen = set()

    for experience in experiences:

        key = (
            experience.get("position"),
            experience.get("company"),
            experience.get("start_date"),
            experience.get("end_date"),
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(experience)

    return unique


# =========================================================
# Total experience
# =========================================================

def calculate_total_experience(experiences):

    if not experiences:
        return None

    intervals = []

    for experience in experiences:

        start = experience.get("start_date")
        end = experience.get("end_date")

        if not start or not end:
            continue

        try:
            start_dt = datetime.strptime(
                start,
                "%Y-%m",
            )

            end_dt = datetime.strptime(
                end,
                "%Y-%m",
            )

        except ValueError:
            continue

        if end_dt < start_dt:
            continue

        intervals.append(
            (start_dt, end_dt)
        )

    if not intervals:
        return None

    intervals.sort(key=lambda x: x[0])

    merged = []

    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:

        if start <= current_end:

            if end > current_end:
                current_end = end

        else:

            merged.append(
                (current_start, current_end)
            )

            current_start = start
            current_end = end

    merged.append(
        (current_start, current_end)
    )

    total_months = 0

    for start, end in merged:

        months = (
            (end.year - start.year) * 12
            + (end.month - start.month)
        )

        total_months += months

    return round(
        total_months / 12,
        2,
    )
