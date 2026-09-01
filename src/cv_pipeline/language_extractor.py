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

    if not text:
        return None

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

    return None


def extract_languages(section_text: str):

    if not section_text:
        return []

    section_text = normalize_text(section_text)

    languages = load_languages()

    results = []

    # ---------------------------------------------------------
    # Process each line independently
    #
    # This is important because proficiency belongs to the
    # language on the same CV line.
    # ---------------------------------------------------------

    for line in section_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore separator-only lines
        if re.fullmatch(r"[\|\-–—•·]+", line):
            continue

        for canonical_name, aliases in languages.items():

            found = False

            for alias in aliases:

                pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

                if re.search(
                    pattern,
                    line,
                    re.IGNORECASE,
                ):
                    found = True
                    break

            if not found:
                continue

            # -------------------------------------------------
            # The language was found on this line.
            #
            # Everything after the language occurrence is the
            # most relevant place to look for proficiency.
            # -------------------------------------------------

            match = None

            for alias in aliases:

                pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

                m = re.search(
                    pattern,
                    line,
                    re.IGNORECASE,
                )

                if m:
                    match = m
                    break

            if not match:
                continue

            context = line[match.end():]
            
            # Only inspect text up to the next language.
            # This prevents a proficiency belonging to another
            # language from being assigned to the current language.
            
            next_language_start = len(context)
            
            for other_canonical, other_aliases in languages.items():
            
                # Ignore other aliases belonging to the SAME language.
                # Example:
                # German/Deutsch
                #
                # German and Deutsch are both the same language,
                # so Deutsch must not terminate German's context.
            
                if other_canonical == canonical_name:
                    continue
            
                for other_alias in other_aliases:
            
                    next_match = re.search(
                        rf"(?<!\w){re.escape(other_alias)}(?!\w)",
                        context,
                        re.IGNORECASE,
                    )
            
                    if next_match:
                        next_language_start = min(
                            next_language_start,
                            next_match.start(),
                        )            
           
            language_context = context[:next_language_start]
            
            level = find_level(language_context)
            results.append(
                {
                    "language": canonical_name,
                    "level": level,
                }
            )

    # ---------------------------------------------------------
    # Remove duplicates
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
