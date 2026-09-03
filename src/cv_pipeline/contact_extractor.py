from __future__ import annotations

import re

from .text_normalizer import (
    normalize_line,
    is_pdf_artifact,
)


# ---------------------------------------------------------------------------
# Regular expressions
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)


# Broad phone pattern.
#
# IMPORTANT:
# Date-shaped strings are filtered separately in _extract_phone().
#
PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d[\d\s()./-]{7,}\d)"
    r"(?!\d)"
)


LINKEDIN_RE = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"linkedin\.com/in/[A-Za-z0-9._%/-]+",
    re.IGNORECASE,
)


GITHUB_RE = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"github\.com/[A-Za-z0-9._%/-]+",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Date of birth patterns
# ---------------------------------------------------------------------------

# Common date formats found in CVs.
#
# Examples:
#   31/01/1998
#   31.01.1998
#   31-01-1998
#   31/1/1998
#   31.1.1998
#
DATE_PATTERN = (
    r"(?:"
    r"(?:0?[1-9]|[12]\d|3[01])"
    r"[./-]"
    r"(?:0?[1-9]|1[0-2])"
    r"[./-]"
    r"(?:19|20)\d{2}"
    r")"
)

DATE_RE = re.compile(
    rf"(?<!\d){DATE_PATTERN}(?!\d)"
)


# Explicit labels strongly indicating date of birth.
#
# English:
#   Date of Birth
#   DOB
#   Birth Date
#   Born
#
# German:
#   Geburtsdatum
#   Geburtstag
#   Geboren
#
DOB_LABEL_RE = re.compile(
    r"\b(?:"
    r"date\s+of\s+birth|"
    r"birth\s+date|"
    r"dob|"
    r"date\s+born|"
    r"born|"
    r"geburtsdatum|"
    r"geburtstag|"
    r"geboren"
    r")\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Words that strongly suggest this is not a person's name.
# ---------------------------------------------------------------------------

NON_NAME_WORDS = {

    "ingenieur",
    "engineer",
    "engineering",
    "developer",
    "entwickler",
    "manager",
    "assistant",
    "professor",
    "student",
    "graduate",
    "master",
    "bachelor",
    "robotic",
    "systems",
    "software",
    "mechanical",
    "computer",
    "science",
    "personal",
    "daten",
    "data",
    "profil",
    "profile",
}


# ---------------------------------------------------------------------------
# General cleaning
# ---------------------------------------------------------------------------

def _clean_contact_value(value: str) -> str | None:

    if not value:
        return None

    value = normalize_line(value)

    return value or None


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def _extract_email(text: str) -> str | None:

    match = EMAIL_RE.search(text)

    if not match:
        return None

    return match.group(0)


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _normalize_date(date_value: str) -> str | None:
    """
    Normalize common date separators.

    Examples:

        31/01/1998 -> 31/01/1998
        31.01.1998 -> 31/01/1998
        31-01-1998 -> 31/01/1998

    The extracted value is intentionally kept in DD/MM/YYYY format.
    """

    if not date_value:
        return None

    date_value = date_value.strip()

    date_value = re.sub(
        r"[.-]",
        "/",
        date_value,
    )

    return date_value


def _is_date_like(value: str) -> bool:
    """
    Return True when a string looks like a calendar date.

    This is particularly important because the broad phone
    regex can otherwise interpret:

        31/01/1998

    as a phone number.
    """

    if not value:
        return False

    value = value.strip()

    return bool(
        DATE_RE.fullmatch(value)
    )


# ---------------------------------------------------------------------------
# Date of birth extraction
# ---------------------------------------------------------------------------

def _extract_date_of_birth(text: str) -> str | None:
    """
    Extract date of birth from a CV.

    Priority:

        1. Explicit DOB label + nearby date
        2. Common DOB labels anywhere in the text
        3. Do NOT blindly return the first date in the CV

    Examples handled:

        Geburtsdatum: 31/01/1998
        Date of Birth: 31.01.1998
        DOB: 31-01-1998
        Born: 31/01/1998
        Geboren: 31.01.1998

    This intentionally does NOT return arbitrary dates such as:

        Jan 2025 - Dec 2025
        2026
        2019
    """

    if not text:
        return None

    # ---------------------------------------------------------------
    # First priority:
    # explicit label followed by a date
    # ---------------------------------------------------------------

    labeled_pattern = re.compile(
        rf"\b(?:"
        r"date\s+of\s+birth|"
        r"birth\s+date|"
        r"dob|"
        r"date\s+born|"
        r"born|"
        r"geburtsdatum|"
        r"geburtstag|"
        r"geboren"
        r")"
        rf"\s*(?:[:=\-]|\s)\s*"
        rf"({DATE_PATTERN})",
        re.IGNORECASE,
    )

    match = labeled_pattern.search(text)

    if match:
        return _normalize_date(
            match.group(1)
        )

    # ---------------------------------------------------------------
    # Second priority:
    # search line-by-line.
    #
    # This handles PDF extraction such as:
    #
    # Geburtsdatum
    # 31/01/1998
    #
    # ---------------------------------------------------------------

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    for i, line in enumerate(lines):

        if not DOB_LABEL_RE.search(line):
            continue

        # Date on the same line.
        match = DATE_RE.search(line)

        if match:
            return _normalize_date(
                match.group(0)
            )

        # Date on the next line.
        if i + 1 < len(lines):

            next_line = lines[i + 1]

            match = DATE_RE.search(
                next_line
            )

            if match:
                return _normalize_date(
                    match.group(0)
                )

    # ---------------------------------------------------------------
    # No explicit DOB label -> do not guess.
    # ---------------------------------------------------------------

    return None


# ---------------------------------------------------------------------------
# Phone
# ---------------------------------------------------------------------------

def _extract_phone(text: str) -> str | None:
    """
    Extract a phone number while avoiding date-shaped values.

    Examples:

        +49-162-975-0578
        +49 162 975 0578
        +49 (162) 9750578
        0241 1234567

    A value such as:

        31/01/1998

    is explicitly rejected as a date.
    """

    if not text:
        return None

    matches = PHONE_RE.finditer(text)

    for match in matches:

        phone = match.group(0).strip()

        # -----------------------------------------------------------
        # Reject dates.
        # -----------------------------------------------------------

        if _is_date_like(phone):
            continue

        # -----------------------------------------------------------
        # Remove whitespace/punctuation and count digits.
        # -----------------------------------------------------------

        digits = re.sub(
            r"\D",
            "",
            phone,
        )

        # Phone numbers should contain a reasonable
        # number of digits.
        if len(digits) < 8:
            continue

        if len(digits) > 15:
            continue

        # -----------------------------------------------------------
        # Additional protection against date-like strings.
        #
        # Examples:
        #
        # 31/01/1998
        # 31-01-1998
        # 31.01.1998
        #
        # -----------------------------------------------------------

        if re.fullmatch(
            r"\d{1,2}[./-]\d{1,2}[./-]\d{4}",
            phone,
        ):
            continue

        return phone

    return None


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------

def _extract_linkedin(text: str) -> str | None:

    match = LINKEDIN_RE.search(text)

    if not match:
        return None

    value = match.group(0)

    if not value.lower().startswith("http"):
        value = "https://" + value

    return value


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

def _extract_github(text: str) -> str | None:

    match = GITHUB_RE.search(text)

    if not match:
        return None

    value = match.group(0)

    if not value.lower().startswith("http"):
        value = "https://" + value

    return value


# ---------------------------------------------------------------------------
# Name detection
# ---------------------------------------------------------------------------

def _looks_like_name(line: str) -> bool:

    line = normalize_line(line)

    if not line:
        return False

    if is_pdf_artifact(line):
        return False

    # Names normally have 2-4 words.
    words = line.split()

    if not 2 <= len(words) <= 4:
        return False

    # Don't consider very long lines.
    if len(line) > 50:
        return False

    # Reject contact information.
    if EMAIL_RE.search(line):
        return False

    if PHONE_RE.search(line):
        return False

    # Reject obvious URLs.
    if "linkedin" in line.lower():
        return False

    if "github" in line.lower():
        return False

    # Reject obvious job titles / headings.
    lower = line.lower()

    if any(
        word in lower.split()
        for word in NON_NAME_WORDS
    ):
        return False

    # Names should consist primarily of letters.
    if not re.fullmatch(
        r"[A-Za-zÄÖÜäöüßÀ-ÿ'`.-]+"
        r"(?:\s+[A-Za-zÄÖÜäöüßÀ-ÿ'`.-]+){1,3}",
        line,
    ):
        return False

    return True


def _extract_name(lines: list[str]) -> str | None:
    """
    Find a person's name near the beginning of the CV.

    Handles PDFs where first/last names are split:

        Manas
        Mehrotra
        Robotic Systems Ingenieur
    """

    # ---------------------------------------------------------------
    # First look for adjacent lines.
    # ---------------------------------------------------------------

    for i in range(len(lines) - 1):

        first = normalize_line(
            lines[i]
        )

        second = normalize_line(
            lines[i + 1]
        )

        if not first or not second:
            continue

        candidate = f"{first} {second}"

        if _looks_like_name(candidate):
            return candidate

    # ---------------------------------------------------------------
    # Fallback: already combined name on one line.
    # ---------------------------------------------------------------

    for line in lines[:15]:

        if _looks_like_name(line):
            return line

    return None


# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------

def _extract_location(text: str) -> str | None:

    # German postal code + city.
    match = re.search(
        r"\b\d{5}\s+"
        r"([A-Za-zÄÖÜäöüßÀ-ÿ -]+)",
        text,
    )

    if match:

        city = match.group(1)

        city = re.sub(
            r"\(.*?\)",
            "",
            city,
        ).strip()

        if city:
            return f"{city}, Germany"

    # Common explicit country/city combination.
    match = re.search(
        r"\b("
        r"Aachen|"
        r"Berlin|"
        r"Bonn|"
        r"Cologne|"
        r"Köln|"
        r"Düsseldorf|"
        r"Frankfurt|"
        r"Hamburg|"
        r"Hannover|"
        r"Karlsruhe|"
        r"Leipzig|"
        r"Munich|"
        r"München|"
        r"Nuremberg|"
        r"Nürnberg|"
        r"Stuttgart"
        r")\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return (
            f"{match.group(1)}, Germany"
        )

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_contacts(text: str) -> dict:
    """
    Extract contact and personal information from CV text.

    Returns:

        {
            "name": ...,
            "email": ...,
            "phone": ...,
            "linkedin": ...,
            "github": ...,
            "location": ...,
            "date_of_birth": ...
        }
    """

    if not text:
        return {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "location": None,
            "date_of_birth": None,
        }

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    name = _extract_name(lines)

    email = _extract_email(text)

    phone = _extract_phone(text)

    linkedin = _extract_linkedin(text)

    github = _extract_github(text)

    location = _extract_location(text)

    date_of_birth = _extract_date_of_birth(text)

    return {
        "name": _clean_contact_value(name),

        "email": _clean_contact_value(email),

        "phone": _clean_contact_value(phone),

        "linkedin": _clean_contact_value(linkedin),

        "github": _clean_contact_value(github),

        "location": _clean_contact_value(location),

        "date_of_birth": _clean_contact_value(
            date_of_birth
        ),
    }
