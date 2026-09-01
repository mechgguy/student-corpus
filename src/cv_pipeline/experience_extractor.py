# experience_extractor.py

import re
from datetime import date


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


# ---------------------------------------------------------
# Date patterns
# ---------------------------------------------------------

MONTH_NAME = (
    r"(?:"
    r"Jan(?:uary)?|"
    r"Feb(?:ruary)?|"
    r"Mar(?:ch)?|"
    r"Apr(?:il)?|"
    r"May|"
    r"Jun(?:e)?|"
    r"Jul(?:y)?|"
    r"Aug(?:ust)?|"
    r"Sep(?:t(?:ember)?)?|"
    r"Oct(?:ober)?|"
    r"Nov(?:ember)?|"
    r"Dec(?:ember)?"
    r")"
)

YEAR = r"(?:19|20)\d{2}"

DATE_VALUE = rf"(?:{MONTH_NAME}[\s,.-]*{YEAR}|{YEAR}|\d{{1,2}}/\d{{4}})"

END_VALUE = rf"(?:{DATE_VALUE}|Present|Current|Now|seit|heute)"


DATE_RANGE_PATTERN = re.compile(
    rf"""
    (?P<start>
        {DATE_VALUE}
    )
    \s*
    (?:-|–|—|to|bis)
    \s*
    (?P<end>
        {END_VALUE}
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# A single year/month such as:
# 2020
# 10/2022
# seit 10/2022
SINGLE_DATE_PATTERN = re.compile(
    rf"""
    (?:
        (?P<month>\d{{1,2}})
        /
        (?P<year>{YEAR})
    )
    |
    (?P<year_only>{YEAR})
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ---------------------------------------------------------
# Date parsing
# ---------------------------------------------------------

def parse_date(value: str):
    """
    Convert a CV date into YYYY-MM.

    Examples:
        January 2025 -> 2025-01
        Jan 2025     -> 2025-01
        08/2023      -> 2023-08
        2020         -> 2020-01
        Present      -> current YYYY-MM
    """

    if not value:
        return None

    value = value.strip().lower()

    if value in {
        "present",
        "current",
        "now",
        "seit",
        "heute",
    }:
        today = date.today()
        return f"{today.year:04d}-{today.month:02d}"

    # MM/YYYY
    match = re.fullmatch(
        r"(\d{1,2})/((?:19|20)\d{2})",
        value,
    )

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}"

    # YYYY
    match = re.search(
        rf"\b((?:19|20)\d{{2}})\b",
        value,
    )

    if not match:
        return None

    year = int(match.group(1))
    month = 1

    for name, number in MONTHS.items():

        if re.search(
            rf"\b{name}\b",
            value,
            re.IGNORECASE,
        ):
            month = number
            break

    return f"{year:04d}-{month:02d}"


# ---------------------------------------------------------
# Duration
# ---------------------------------------------------------

def calculate_duration(start, end):

    if not start or not end:
        return None

    try:

        start_year, start_month = map(
            int,
            start.split("-"),
        )

        end_year, end_month = map(
            int,
            end.split("-"),
        )

    except (
        ValueError,
        AttributeError,
    ):
        return None

    months = (
        (end_year - start_year) * 12
        + (end_month - start_month)
    )

    if months < 0:
        return None

    return round(
        months / 12,
        2,
    )


# ---------------------------------------------------------
# Experience extraction
# ---------------------------------------------------------

def extract_experience(section_text: str):

    if not section_text:
        return []

    lines = [
        line.strip()
        for line in section_text.splitlines()
        if line.strip()
    ]

    results = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # -------------------------------------------------
        # Case 1:
        # A full date range is on this line
        #
        # 08/2023 – 01/2025
        # Jan 2020 - Present
        # 2019 - 2021
        # -------------------------------------------------

        match = DATE_RANGE_PATTERN.search(line)

        if match:

            start = parse_date(
                match.group("start")
            )

            end = parse_date(
                match.group("end")
            )

            duration = calculate_duration(
                start,
                end,
            )

            # Previous line is normally the company
            # or position.
            previous = lines[i - 1] if i > 0 else None
            previous_previous = (
                lines[i - 2]
                if i > 1
                else None
            )

            position = previous_previous
            company = previous

            # If only one line exists before the date,
            # don't invent a company.
            if i == 0:
                position = None
                company = None

            results.append(
                {
                    "position": position,
                    "company": company,
                    "location": None,
                    "start_date": start,
                    "end_date": end,
                    "description": None,
                    "duration_years": duration,
                }
            )

            i += 1
            continue

        # -------------------------------------------------
        # Case 2:
        # Single year date
        #
        # 2020
        #
        # This is common in CVs.
        # -------------------------------------------------

        single = SINGLE_DATE_PATTERN.fullmatch(
            line
        )

        if single:

            date_value = parse_date(line)

            # Look backwards for likely position/company.
            previous = (
                lines[i - 1]
                if i > 0
                else None
            )

            previous_previous = (
                lines[i - 2]
                if i > 1
                else None
            )

            # Look ahead for company/location.
            next_line = (
                lines[i + 1]
                if i + 1 < len(lines)
                else None
            )

            next_next_line = (
                lines[i + 2]
                if i + 2 < len(lines)
                else None
            )

            position = previous
            company = next_line

            # If the next line looks like a location,
            # use the following line as company.
            if (
                next_line
                and (
                    "," in next_line
                    or next_line.lower()
                    in {
                        "china",
                        "germany",
                        "india",
                    }
                )
            ):
                company = next_next_line

            results.append(
                {
                    "position": position,
                    "company": company,
                    "location": None,
                    "start_date": date_value,
                    "end_date": date_value,
                    "description": None,
                    "duration_years": 0.0,
                }
            )

        i += 1

    return results


# ---------------------------------------------------------
# Total experience
# ---------------------------------------------------------

def calculate_total_experience(experience):

    intervals = []

    for job in experience:

        start = job.get("start_date")
        end = job.get("end_date")

        if not start or not end:
            continue

        try:

            start_year, start_month = map(
                int,
                start.split("-"),
            )

            end_year, end_month = map(
                int,
                end.split("-"),
            )

        except (
            ValueError,
            AttributeError,
        ):
            continue

        start_index = (
            start_year * 12
            + start_month
        )

        end_index = (
            end_year * 12
            + end_month
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
        return None

    intervals.sort()

    merged = []

    for start, end in intervals:

        if (
            not merged
            or start > merged[-1][1]
        ):
            merged.append(
                [start, end]
            )

        else:
            merged[-1][1] = max(
                merged[-1][1],
                end,
            )

    total_months = sum(
        end - start
        for start, end in merged
    )

    return round(
        total_months / 12,
        2,
    )
