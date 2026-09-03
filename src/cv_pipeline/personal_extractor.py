import re


# =========================================================
# Generic cleaning
# =========================================================

def _clean(value):
    if not value:
        return None

    value = value.strip()

    value = re.sub(
        r"^[\s:;,.|\-–—]+",
        "",
        value,
    )

    value = re.sub(
        r"[\s:;,.|\-–—]+$",
        "",
        value,
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip() or None


# =========================================================
# Nationality
# =========================================================

NATIONALITY_PATTERNS = [
    re.compile(
        r"\b(?:nationality|citizenship)\s*[:\-]?\s*(.+)",
        re.IGNORECASE,
    ),

    re.compile(
        r"\b(?:nationalität|staatsangehörigkeit)\s*[:\-]?\s*(.+)",
        re.IGNORECASE,
    ),
]


def extract_nationality(text):
    """
    Extract nationality from a CV.

    Examples:

        Nationality: Chinese
        Nationality Chinese
        Nationalität: Indien
        Staatsangehörigkeit: Deutsch
        Citizenship: Indian
    """

    if not text:
        return None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        for pattern in NATIONALITY_PATTERNS:

            match = pattern.search(line)

            if not match:
                continue

            value = _clean(match.group(1))

            if value:
                return value

    return None


# =========================================================
# Name detection
# =========================================================

NAME_LABEL_PATTERN = re.compile(
    r"^\s*(?:name|full name|vorname|nachname|"
    r"vollständiger name)\s*[:\-]\s*(.+)$",
    re.IGNORECASE,
)


NAME_REJECT_PATTERNS = [
    # CV/document headings
    r"^curriculum vitae$",
    r"^cv$",
    r"^resume$",
    r"^résumé$",
    r"^lebenslauf$",

    # Section headings
    r"^personal data$",
    r"^personal details$",
    r"^persönliche daten$",
    r"^contact$",
    r"^contact details$",
    r"^kontakt$",

    # Common headings
    r"^profile$",
    r"^profil$",
    r"^about me$",
    r"^über mich$",
    r"^education$",
    r"^ausbildung$",
    r"^experience$",
    r"^berufserfahrung$",
    r"^skills$",
    r"^fähigkeiten$",
    r"^languages$",
    r"^sprachen$",
    r"^projects$",
    r"^projekte$",
    r"^certifications$",
    r"^zertifikate.*$",

    # Nationality
    r"^nationality.*$",
    r"^nationalität.*$",
    r"^citizenship.*$",
    r"^staatsangehörigkeit.*$",

    # Contact information
    r"^email.*$",
    r"^e-mail.*$",
    r"^phone.*$",
    r"^telefon.*$",
    r"^mobile.*$",
    r"^mobil.*$",
    r"^tel.*$",

    # URLs
    r"^https?://.*$",
    r"^www\..*$",

    # Degree / job titles
    r"^.*\b(?:bachelor|master|m\.?sc|b\.?sc|phd|doktor)\b.*$",
]


def _looks_like_rejected_name(line):
    """
    Reject obvious headings, labels, URLs and non-name lines.
    """

    lower = line.lower().strip()

    for pattern in NAME_REJECT_PATTERNS:

        if re.fullmatch(pattern, lower, re.IGNORECASE):
            return True

    return False


def _looks_like_name(line):
    """
    Heuristic check whether a line looks like a person's name.
    """

    if not line:
        return False

    line = _clean(line)

    if not line:
        return False

    if _looks_like_rejected_name(line):
        return False

    # Too long to realistically be a person's name.
    if len(line) > 80:
        return False

    # Names normally contain at least one alphabetic character.
    if not re.search(r"[A-Za-zÄÖÜäöüßÀ-ÿ]", line):
        return False

    # Reject email addresses.
    if "@" in line:
        return False

    # Reject URLs.
    if re.search(r"https?://|www\.", line, re.IGNORECASE):
        return False

    # Reject phone numbers / mostly numeric strings.
    digits = len(re.findall(r"\d", line))

    if digits > 2:
        return False

    # Reject obvious labels.
    if re.match(
        r"^(name|email|phone|tel|mobile|"
        r"nationality|nationalität|"
        r"date of birth|geburtsdatum)\b",
        line,
        re.IGNORECASE,
    ):
        return False

    # Reject lines with too many punctuation characters.
    punctuation = len(
        re.findall(r"[^A-Za-zÄÖÜäöüßÀ-ÿ\s'.\-]", line)
    )

    if punctuation > 2:
        return False

    # A person's name normally has 2-5 words.
    words = line.split()

    if not 2 <= len(words) <= 5:
        return False

    return True


def _name_score(line, index):
    """
    Score a possible name.

    Higher score = more likely to be a person's name.
    """

    if not _looks_like_name(line):
        return -999

    words = line.split()

    score = 0

    # Strong signal: 2-4 name-like words.
    if 2 <= len(words) <= 4:
        score += 5

    # Names usually use capitalization.
    capitalized = sum(
        1
        for word in words
        if word[:1].isupper()
    )

    if capitalized == len(words):
        score += 4

    elif capitalized >= 2:
        score += 2

    # Early in the CV is generally a strong signal.
    if index < 5:
        score += 3

    elif index < 10:
        score += 1

    # Penalize phrases that look like sentences.
    if re.search(
        r"\b(?:engineer|developer|manager|student|"
        r"graduate|specialist|consultant|scientist)\b",
        line,
        re.IGNORECASE,
    ):
        score -= 5

    return score


def extract_name(text):
    """
    Robustly extract a person's name from CV text.

    Priority:

        1. Explicit "Name:" field
        2. Strong candidate near beginning of CV
        3. First plausible name-like line
    """

    if not text:
        return None

    lines = [
        _clean(line)
        for line in text.splitlines()
        if _clean(line)
    ]

    if not lines:
        return None

    # -----------------------------------------------------
    # 1. Explicit name field
    # -----------------------------------------------------

    for line in lines[:30]:

        match = NAME_LABEL_PATTERN.match(line)

        if match:

            candidate = _clean(match.group(1))

            if _looks_like_name(candidate):
                return candidate

    # -----------------------------------------------------
    # 2. Score candidates
    #
    # Only inspect the beginning of the CV.
    # This prevents names appearing in references,
    # publications, etc. from being selected.
    # -----------------------------------------------------

    candidates = []

    for index, line in enumerate(lines[:25]):

        score = _name_score(
            line,
            index,
        )

        if score > 0:

            candidates.append(
                (
                    score,
                    index,
                    line,
                )
            )

    if candidates:

        candidates.sort(
            key=lambda x: (
                -x[0],
                x[1],
            )
        )

        return candidates[0][2]

    return None


