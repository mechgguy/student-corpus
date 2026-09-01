
import re


SECTION_PATTERNS = {
    "summary": [
        r"summary",
        r"profile",
        r"profil",
        r"professional profile",
        r"about me",
        r"objective",
        r"professional summary",
    ],

    "experience": [
        r"experience",
        r"work experience",
        r"professional experience",
        r"employment history",
        r"career history",
        r"professional background",
        r"work history",

        # German
        r"berufserfahrung",
        r"berufliche erfahrung",
        r"beruflicher werdegang",
        r"praktische erfahrung",
    ],

    "education": [
        r"education",
        r"academic background",
        r"academic qualifications",
        r"educational background",

        # German
        r"ausbildung",
        r"akademische ausbildung",
        r"studium",
        r"hochschulbildung",
    ],

    "skills": [
        r"skills",
        r"technical skills",
        r"technical expertise",
        r"core competencies",
        r"competencies",
        r"expertise",

        # German
        r"kenntnisse",
        r"fachkenntnisse",
        r"technische kenntnisse",
        r"kompetenzen",
        r"fähigkeiten",
    ],

    "languages": [
        r"languages",
        r"language skills",
        r"linguistic skills",

        # German
        r"sprachen",
        r"sprachkenntnisse",
        r"sprachkenntnisse und kompetenzen",
    ],

    "certifications": [
        r"certifications",
        r"certificates",
        r"professional certifications",
        r"publications and certifications",
        r"publications & certifications",
        r"publications and certificates",
        r"publications & certificates",

        # German
        r"zertifikate",
        r"zertifizierungen",
        r"weiterbildungen",
    ],

    "projects": [
        r"projects",
        r"academic projects",
        r"personal projects",
        r"selected projects",
        r"project experience",
        r"university project",
        r"university projects",

        # German
        r"projekterfahrung",
        r"projekte",
        r"akademische projekte",
    ],

    "awards": [
        r"awards",
        r"award",
        r"awards and leadership",
        r"award and leadership",
        r"award & leadership",
        r"awards & leadership",
        r"honors",
        r"honours",
        r"leadership",
        r"achievements",

        # German
        r"auszeichnungen",
        r"preise",
        r"ehrenamt",
    ],
}


def normalize_heading(line: str) -> str:
    """
    Normalize a possible CV section heading.
    """

    value = line.strip().lower()

    # Remove common bullet/decorative characters.
    value = re.sub(
        r"^[\s•·\-–—|]+",
        "",
        value,
    )

    # Normalize ampersand.
    value = value.replace("&", " and ")

    # Remove punctuation while keeping German characters.
    value = re.sub(
        r"[^a-zA-ZäöüÄÖÜß ]",
        "",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def detect_section(line: str) -> str | None:

    normalized = normalize_heading(line)

    if not normalized:
        return None

    for section, patterns in SECTION_PATTERNS.items():

        for pattern in patterns:

            if re.fullmatch(
                pattern,
                normalized,
                re.IGNORECASE,
            ):
                return section

    return None


def split_sections(text: str) -> dict[str, str]:

    sections = {}
    current_section = "header"

    sections[current_section] = []

    for line in text.splitlines():

        section = detect_section(line)

        if section:

            current_section = section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
    }


