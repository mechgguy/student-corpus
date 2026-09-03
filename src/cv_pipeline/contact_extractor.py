from __future__ import annotations

import re

from .text_normalizer import (
    normalize_line,
    is_pdf_artifact,
)


# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# PHONE
# ---------------------------------------------------------------------------

PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d[\d\s()./-]{7,}\d)"
    r"(?!\d)"
)


# ---------------------------------------------------------------------------
# LINKEDIN / GITHUB
# ---------------------------------------------------------------------------
#
# These patterns intentionally support:
#
#   https://www.linkedin.com/in/username
#   https://linkedin.com/in/username
#   www.linkedin.com/in/username
#   linkedin.com/in/username
#
# They are primarily used when an actual URL exists in extracted PDF text.
#
# Username-only extraction is handled separately below because:
#
#   /username
#   username
#
# is ambiguous without the surrounding "LinkedIn" / "GitHub" label.
# ---------------------------------------------------------------------------

LINKEDIN_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"linkedin\.com/in/"
    r"([A-Za-z0-9._%-]+)",
    re.IGNORECASE,
)

GITHUB_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"github\.com/"
    r"([A-Za-z0-9._%-]+)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# LABELLED PROFILE LINKS
# ---------------------------------------------------------------------------
#
# Handles examples such as:
#
#   LinkedIn: /manas-mehrotraa
#   LinkedIn /manas-mehrotraa
#   LinkedIn: manas-mehrotraa
#   LinkedIn: linkedin.com/in/manas-mehrotraa
#
# The label is important because a bare username by itself is ambiguous.
# ---------------------------------------------------------------------------

LINKEDIN_LABEL_RE = re.compile(
    r"\blinkedin\b"
    r"\s*(?:profile|url|link)?"
    r"\s*[:\-]?\s*"
    r"(?:https?://)?"
    r"(?:www\.)?"
    r"(?:linkedin\.com/in/)?"
    r"[/]?"
    r"([A-Za-z0-9][A-Za-z0-9._%-]{1,99})",
    re.IGNORECASE,
)

GITHUB_LABEL_RE = re.compile(
    r"\bgithub\b"
    r"\s*(?:profile|url|link)?"
    r"\s*[:\-]?\s*"
    r"(?:https?://)?"
    r"(?:www\.)?"
    r"(?:github\.com/)?"
    r"[/]?"
    r"([A-Za-z0-9][A-Za-z0-9._%-]{1,99})",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# WORDS THAT STRONGLY SUGGEST THIS IS NOT A PERSON'S NAME
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
# GENERAL CLEANING
# ---------------------------------------------------------------------------

def _clean_contact_value(value: str) -> str | None:
    if not value:
        return None

    value = normalize_line(value)

    return value or None


# ---------------------------------------------------------------------------
# EMAIL
# ---------------------------------------------------------------------------

def _extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)

    if not match:
        return None

    return match.group(0)


# ---------------------------------------------------------------------------
# PHONE
# ---------------------------------------------------------------------------

def _extract_phone(text: str) -> str | None:
    """
    Extract a phone number while avoiding dates such as:

        31/01/1998
        2025-01-01
    """

    for match in PHONE_RE.finditer(text):

        phone = match.group(0).strip()

        digits = re.sub(r"\D", "", phone)

        # A realistic phone number should contain enough digits.
        if len(digits) < 8:
            continue

        # Reject obvious date formats.
        if re.fullmatch(
            r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}",
            phone,
        ):
            continue

        if re.fullmatch(
            r"\d{4}[./-]\d{1,2}[./-]\d{1,2}",
            phone,
        ):
            continue

        return phone

    return None


# ---------------------------------------------------------------------------
# DATE OF BIRTH
# ---------------------------------------------------------------------------

DATE_OF_BIRTH_LABEL_RE = re.compile(
    r"""
    \b
    (?:
        date\s+of\s+birth
        |
        birth\s*date
        |
        geboren
        |
        geburtsdatum
        |
        geburts\s*datum
        |
        dob
    )
    \s*
    [:.\-]?
    \s*
    (
        \d{1,2}[./-]\d{1,2}[./-]\d{2,4}
        |
        \d{4}[./-]\d{1,2}[./-]\d{1,2}
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _extract_date_of_birth(text: str) -> str | None:
    """
    Extract date of birth only when it is associated with a DOB label.

    Examples:

        Geburtsdatum: 31/01/1998
        Date of Birth: 31/01/1998
        DOB: 31-01-1998

    This prevents ordinary dates in education/experience sections
    from being mistaken for a date of birth.
    """

    match = DATE_OF_BIRTH_LABEL_RE.search(text)

    if not match:
        return None

    return match.group(1).strip()


# ---------------------------------------------------------------------------
# PROFILE URL NORMALIZATION
# ---------------------------------------------------------------------------

def _normalize_linkedin_username(username: str) -> str | None:
    """
    Convert a LinkedIn username into a canonical URL.
    """

    if not username:
        return None

    username = username.strip().strip("/")

    if not username:
        return None

    return f"https://www.linkedin.com/in/{username}"


def _normalize_github_username(username: str) -> str | None:
    """
    Convert a GitHub username into a canonical URL.
    """

    if not username:
        return None

    username = username.strip().strip("/")

    if not username:
        return None

    return f"https://github.com/{username}"


# ---------------------------------------------------------------------------
# LINKEDIN
# ---------------------------------------------------------------------------

def _extract_linkedin(text: str) -> str | None:
    """
    Extract LinkedIn profile from:

        https://www.linkedin.com/in/username
        https://linkedin.com/in/username
        www.linkedin.com/in/username
        linkedin.com/in/username

    or labelled username forms:

        LinkedIn: /username
        LinkedIn: username
        LinkedIn /username

    Returns a canonical URL.
    """

    # ---------------------------------------------------------
    # 1. Full / partial LinkedIn URL
    # ---------------------------------------------------------

    match = LINKEDIN_URL_RE.search(text)

    if match:
        return _normalize_linkedin_username(match.group(1))

    # ---------------------------------------------------------
    # 2. Labelled username
    # ---------------------------------------------------------

    match = LINKEDIN_LABEL_RE.search(text)

    if match:
        username = match.group(1)

        # Avoid accidentally treating words after "LinkedIn"
        # as usernames when they clearly are not.
        if username.lower() not in {
            "linkedin",
            "profile",
            "url",
            "link",
        }:
            return _normalize_linkedin_username(username)

    return None


# ---------------------------------------------------------------------------
# GITHUB
# ---------------------------------------------------------------------------

def _extract_github(text: str) -> str | None:
    """
    Extract GitHub profile from:

        https://github.com/username
        https://www.github.com/username
        www.github.com/username
        github.com/username

    or labelled username forms:

        GitHub: /username
        GitHub: username
        GitHub /username

    Returns a canonical URL.
    """

    # ---------------------------------------------------------
    # 1. Full / partial GitHub URL
    # ---------------------------------------------------------

    match = GITHUB_URL_RE.search(text)

    if match:
        return _normalize_github_username(match.group(1))

    # ---------------------------------------------------------
    # 2. Labelled username
    # ---------------------------------------------------------

    match = GITHUB_LABEL_RE.search(text)

    if match:
        username = match.group(1)

        if username.lower() not in {
            "github",
            "profile",
            "url",
            "link",
        }:
            return _normalize_github_username(username)

    return None


# ---------------------------------------------------------------------------
# NAME DETECTION
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
    lower = line.lower()

    if "linkedin" in lower:
        return False

    if "github" in lower:
        return False

    # Reject obvious job titles / headings.
    if any(word in lower.split() for word in NON_NAME_WORDS):
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

    # ---------------------------------------------------------
    # 1. Adjacent lines
    # ---------------------------------------------------------

    for i in range(len(lines) - 1):

        first = normalize_line(lines[i])
        second = normalize_line(lines[i + 1])

        if not first or not second:
            continue

        candidate = f"{first} {second}"

        if _looks_like_name(candidate):
            return candidate

    # ---------------------------------------------------------
    # 2. Already combined name
    # ---------------------------------------------------------

    for line in lines[:15]:

        if _looks_like_name(line):
            return line

    return None


# ---------------------------------------------------------------------------
# LOCATION
# ---------------------------------------------------------------------------

def _extract_location(text: str) -> str | None:

    # German postal code + city.
    match = re.search(
        r"\b\d{5}\s+([A-Za-zÄÖÜäöüßÀ-ÿ -]+)",
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
        r"Aachen|Berlin|Bonn|Cologne|Köln|"
        r"Düsseldorf|Frankfurt|Hamburg|Hannover|"
        r"Karlsruhe|Leipzig|Munich|München|"
        r"Nuremberg|Nürnberg|Stuttgart"
        r")\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return f"{match.group(1)}, Germany"

    return None


# ---------------------------------------------------------------------------
# MAIN CONTACT EXTRACTION
# ---------------------------------------------------------------------------

def extract_contacts(text: str) -> dict:

    if not text:
        return {
            "name": None,
            "date_of_birth": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "location": None,
        }

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    # ---------------------------------------------------------
    # Extract fields
    # ---------------------------------------------------------

    name = _extract_name(lines)

    date_of_birth = _extract_date_of_birth(text)

    email = _extract_email(text)

    phone = _extract_phone(text)

    linkedin = _extract_linkedin(text)

    github = _extract_github(text)

    location = _extract_location(text)

    # ---------------------------------------------------------
    # Return
    # ---------------------------------------------------------

    return {
        "name": _clean_contact_value(name),

        "date_of_birth": _clean_contact_value(
            date_of_birth
        ),

        "email": _clean_contact_value(email),

        "phone": _clean_contact_value(phone),

        "linkedin": _clean_contact_value(linkedin),

        "github": _clean_contact_value(github),

        "location": _clean_contact_value(location),
    }
