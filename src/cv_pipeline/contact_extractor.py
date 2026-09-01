import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"""
    (?<!\d)
    (?:
        \+?\d{1,3}[\s.-]?
    )?
    (?:
        \(?\d{2,4}\)?[\s.-]?
    )?
    \d{3,4}[\s.-]?\d{3,4}
    (?!\d)
    """,
    re.VERBOSE,
)

LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9._%-]+",
    re.IGNORECASE,
)

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9._%-]+",
    re.IGNORECASE,
)


def extract_email(text: str):
    match = EMAIL_PATTERN.search(text)

    return match.group(0) if match else None


def extract_phone(text: str):
    matches = PHONE_PATTERN.findall(text)

    if not matches:
        return None

    # Clean whitespace
    candidates = [
        re.sub(r"\s+", " ", match).strip()
        for match in matches
    ]

    # Prefer longer phone-like strings
    candidates.sort(key=len, reverse=True)

    return candidates[0]


def extract_linkedin(text: str):
    match = LINKEDIN_PATTERN.search(text)

    if not match:
        return None

    return match.group(0)


def extract_github(text: str):
    match = GITHUB_PATTERN.search(text)

    if not match:
        return None

    return match.group(0)


def extract_name(text: str):
    """
    Heuristic name extraction.

    Usually the candidate name is one of the first few
    meaningful lines of the CV.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:15]:

        # Skip obvious contact information
        if EMAIL_PATTERN.search(line):
            continue

        if PHONE_PATTERN.search(line):
            continue

        if LINKEDIN_PATTERN.search(line):
            continue

        if GITHUB_PATTERN.search(line):
            continue

        # Skip common CV headings
        if line.lower() in {
            "curriculum vitae",
            "resume",
            "cv",
            "profile",
            "personal information",
            "contact",
        }:
            continue

        # Names are generally relatively short
        words = line.split()

        if 2 <= len(words) <= 5:

            # Don't accept lines containing lots of punctuation
            if sum(c.isdigit() for c in line) == 0:

                if len(line) <= 80:
                    return line

    return None


def extract_contacts(text: str):

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
    }
