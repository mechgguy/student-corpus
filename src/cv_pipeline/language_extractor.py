import json
import re
from pathlib import Path


LEVELS = [
    "native",
    "fluent",
    "bilingual",
    "basic",
    "beginner",
    "intermediate",
    "advanced",
    "professional",
    "mother tongue",
    "mother-tongue",
    "muttersprache",
    "fließend",
    "fliessend",
    "grundkenntnisse",
    "gute arbeitskenntnisse",
    "sehr gute arbeitskenntnisse",
    "A1",
    "A2",
    "B1",
    "B2",
    "C1",
    "C2",
]


def load_languages():
    config_path = (
        Path(__file__).resolve().parents[2]
        / "configs"
        / "languages.json"
    )

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    # Remove invisible PDF characters
    text = (
        text
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\ufeff", "")
    )

    return text


def find_level(text: str):
    """
    Find a language proficiency level.

    Priority:
        1. CEFR level: A1-C2
        2. Native / mother tongue
        3. Fluent / bilingual
        4. Other proficiency descriptions
    """

    if not text:
        return "Not Provided"

    # ---------------------------------------------------------
    # 1. CEFR levels have highest priority
    # ---------------------------------------------------------

    match = re.search(
        r"\b(A1|A2|B1|B2|C1|C2)\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).upper()

    # ---------------------------------------------------------
    # 2. Other proficiency descriptions
    # ---------------------------------------------------------

    sorted_levels = sorted(
        LEVELS,
        key=len,
        reverse=True,
    )

    for level in sorted_levels:
        if re.search(
            rf"(?<!\w){re.escape(level)}(?!\w)",
            text,
            re.IGNORECASE,
        ):
            return level

    return "Not Provided"


def _find_language(line: str, languages: dict):
    """
    Return the canonical language name and match object
    if a configured language is found in the line.
    """

    for canonical_name, aliases in languages.items():

        for alias in aliases:

            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

            match = re.search(
                pattern,
                line,
                re.IGNORECASE,
            )

            if match:
                return canonical_name, match

    return None, None


def _contains_language(text: str, languages: dict) -> bool:
    """
    Check whether text contains any configured language.
    """

    if not text:
        return False

    canonical_name, match = _find_language(
        text,
        languages,
    )

    return match is not None


def _extract_language_context(
    lines: list[str],
    index: int,
    match: re.Match,
    languages: dict,
) -> str:
    """
    Extract proficiency context belonging to a language.

    Supports both:

        German C1

    and PDF layouts where the proficiency is placed
    on the following line:

        German
        C1

    We inspect:

        - text after the language on the same line
        - the next few lines

    but stop as soon as another language is encountered.
    """

    context_parts = []

    # ---------------------------------------------------------
    # 1. Text after language on the SAME line
    # ---------------------------------------------------------

    same_line_context = lines[index][match.end():].strip()

    if same_line_context:
        context_parts.append(same_line_context)

    # ---------------------------------------------------------
    # 2. Look at following lines
    #
    # PDF extraction often separates the language and
    # proficiency into different lines.
    # ---------------------------------------------------------

    MAX_FOLLOWING_LINES = 2

    for offset in range(1, MAX_FOLLOWING_LINES + 1):

        next_index = index + offset

        if next_index >= len(lines):
            break

        next_line = lines[next_index].strip()

        if not next_line:
            continue

        # -----------------------------------------------------
        # Stop if another language starts.
        #
        # Example:
        #
        # Deutsch
        # C1
        # Englisch
        # C2
        #
        # C1 belongs to Deutsch, but C2 belongs to Englisch.
        # -----------------------------------------------------

        if _contains_language(
            next_line,
            languages,
        ):
            break

        context_parts.append(next_line)

    return " ".join(context_parts)


def extract_languages(section_text: str):
    """
    Extract languages and proficiency levels from CV text.

    Handles both inline and vertically separated PDF layouts.

    Examples:

        German C1
        English C2

    and:

        German
        C1
        English
        C2

    and:

        German
        fluent
        English
        native speaker
    """

    if not section_text:
        return []

    section_text = normalize_text(section_text)

    languages = load_languages()

    results = []

    # ---------------------------------------------------------
    # Normalize lines
    # ---------------------------------------------------------

    lines = []

    for raw_line in section_text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        # Ignore separator-only lines
        if re.fullmatch(
            r"[\|\-–—•·*]+",
            line,
        ):
            continue

        lines.append(line)

    # ---------------------------------------------------------
    # Process each line
    # ---------------------------------------------------------

    for index, line in enumerate(lines):

        canonical_name, match = _find_language(
            line,
            languages,
        )

        if not match:
            continue

        # -----------------------------------------------------
        # Extract context belonging to this language
        # -----------------------------------------------------

        language_context = _extract_language_context(
            lines=lines,
            index=index,
            match=match,
            languages=languages,
        )

        # -----------------------------------------------------
        # Find proficiency
        # -----------------------------------------------------

        level = find_level(language_context)

        results.append(
            {
                "language": canonical_name,
                "level": level,
            }
        )

    # ---------------------------------------------------------
    # Remove duplicates
    #
    # Keep the first occurrence.
    # ---------------------------------------------------------

    unique_results = []

    seen = set()

    for result in results:

        language = result["language"]

        if language in seen:
            continue

        seen.add(language)

        unique_results.append(result)

    return unique_results