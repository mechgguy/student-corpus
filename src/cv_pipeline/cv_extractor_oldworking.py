import re

from .schemas import Candidate


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\(?\d{2,4}\)?[\s.-]?)?"
    r"\d{3,4}[\s.-]?\d{3,4}"
    r"(?!\d)"
)

LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"linkedin\.com/in/[A-Za-z0-9_-]+",
    re.IGNORECASE,
)

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"github\.com/[A-Za-z0-9_-]+",
    re.IGNORECASE,
)


def find_email(text: str) -> str | None:

    match = EMAIL_PATTERN.search(text)

    return match.group(0) if match else None


def find_phone(text: str) -> str | None:

    match = PHONE_PATTERN.search(text)

    return match.group(0).strip() if match else None


def find_linkedin(text: str) -> str | None:

    match = LINKEDIN_PATTERN.search(text)

    return match.group(0) if match else None


def find_github(text: str) -> str | None:

    match = GITHUB_PATTERN.search(text)

    return match.group(0) if match else None


def find_name(text: str) -> str | None:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:15]:

        if "@" in line:
            continue

        if any(char.isdigit() for char in line):
            continue

        words = line.split()

        if not 2 <= len(words) <= 5:
            continue

        if all(
            re.match(
                r"^[A-Za-zÀ-ÖØ-öø-ÿ'’-]+$",
                word,
            )
            for word in words
        ):
            return line

    return None


def extract_candidate(
    text: str,
    candidate_id: str,
    filename: str,
) -> Candidate:

    return Candidate(
        candidate_id=candidate_id,
        filename=filename,
        name=find_name(text),
        email=find_email(text),
        phone=find_phone(text),
        linkedin=find_linkedin(text),
        github=find_github(text),
        raw_text=text,
    )
