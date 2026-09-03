from __future__ import annotations

import re
import unicodedata


# ---------------------------------------------------------------------------
# Mojibake / encoding repair
# ---------------------------------------------------------------------------

MOJIBAKE_REPLACEMENTS = {
    # German
    "Ã¤": "ä",
    "Ã¶": "ö",
    "Ã¼": "ü",
    "Ã„": "Ä",
    "Ã–": "Ö",
    "Ãœ": "Ü",
    "ÃŸ": "ß",

    # Double-encoded German
    "ÃƒÂ¤": "ä",
    "ÃƒÂ¶": "ö",
    "ÃƒÂ¼": "ü",
    "Ãƒâ€ž": "Ä",
    "Ãƒâ€“": "Ö",
    "ÃƒÅ“": "Ü",
    "ÃƒÅ¸": "ß",

    # French
    "Ã©": "é",
    "Ã¨": "è",
    "Ãª": "ê",
    "Ã«": "ë",
    "Ã ": "à",
    "Ã¢": "â",
    "Ã´": "ô",
    "Ã»": "û",
    "Ã§": "ç",

    # Double-encoded French
    "ÃƒÂ©": "é",
    "ÃƒÂ¨": "è",
    "ÃƒÂª": "ê",
    "ÃƒÂ«": "ë",
    "Ãƒ ": "à",
    "ÃƒÂ¢": "â",
    "ÃƒÂ´": "ô",
    "ÃƒÂ»": "û",
    "ÃƒÂ§": "ç",

    # Dashes / bullets
    "â€“": "-",
    "â€”": "-",
    "âˆ’": "-",
    "â€¢": "•",
    "Â·": "·",

    "Ã¢â‚¬â€œ": "-",
    "Ã¢â‚¬â€": "-",
    "Ã¢Ë†â€™": "-",
    "Ã¢â‚¬Â¢": "•",
    "Ã‚Â·": "·",

    # Remove stray encoding prefix
    "Ã‚": "",
    "Â": "",

    # Ligatures
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ï¬": "fi",
    "ï¬‚": "fl",
}


# ---------------------------------------------------------------------------
# PDF artefact detection
# ---------------------------------------------------------------------------

PDF_ARTIFACTS = {
    # Common isolated PDF extraction symbols
    "•",
    "·",
    "▪",
    "◦",
    "●",
    "○",
    "■",
    "□",
    "◆",
    "◇",
    "►",
    "▶",
    "→",
    "➜",
    "➤",

    # Frequently seen extraction artefacts
    "¥",
    "Ð",
    "Å",
    "Ñ",
    "§",
    "ª",
    "ò",
    "0",
    "P",
    "[",
    "]",
}


def repair_mojibake(text: str) -> str:
    """
    Repair common UTF-8 / Latin-1 / Windows-1252 decoding artefacts.

    Only known problematic sequences are replaced.
    """

    if not text:
        return ""

    result = text

    for broken, fixed in MOJIBAKE_REPLACEMENTS.items():
        result = result.replace(broken, fixed)

    return result


# ---------------------------------------------------------------------------
# PDF artefact helpers
# ---------------------------------------------------------------------------

def is_pdf_artifact(line: str) -> bool:
    """
    Return True when a line appears to contain only a PDF extraction artefact.

    Examples that should be removed:

        ¥
        Ð
        §
        Ñ
        ○○○○○
        0
        [

    Important:
    This function deliberately does NOT remove normal text containing
    punctuation or symbols.
    """

    if not line:
        return True

    value = line.strip()

    if not value:
        return True

    # Remove spaces before testing.
    compact = re.sub(r"\s+", "", value)

    if not compact:
        return True

    # Pure known artefact.
    if compact in PDF_ARTIFACTS:
        return True

    # Repeated artefact symbols such as:
    #
    # ○○○○○
    # ¥¥¥
    # §§
    #
    if len(compact) <= 12:
        unique = set(compact)

        if len(unique) == 1 and next(iter(unique)) in PDF_ARTIFACTS:
            return True

    # Rating dots / circles from CV templates.
    if re.fullmatch(r"[○●•·]{1,10}", compact):
        return True

    return False


def remove_pdf_artifacts(text: str) -> str:
    """
    Remove lines that are clearly PDF extraction artefacts.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        if is_pdf_artifact(line):
            continue

        lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Date / hyphen normalization
# ---------------------------------------------------------------------------

def normalize_dashes(text: str) -> str:
    """
    Normalize Unicode and mojibake dash characters to '-'.
    """

    if not text:
        return ""

    replacements = {
        "–": "-",
        "—": "-",
        "−": "-",
        "-": "-",
        "‒": "-",
        "﹘": "-",
        "﹣": "-",
        "－": "-",

        "â€“": "-",
        "â€”": "-",
        "âˆ’": "-",
        "Ã¢â‚¬â€œ": "-",
        "Ã¢â‚¬â€": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ---------------------------------------------------------------------------
# Line joining helpers
# ---------------------------------------------------------------------------

def fix_hyphenated_line_breaks(text: str) -> str:
    """
    Join words broken across PDF line boundaries.

    Example:

        transform-
        ation

    becomes:

        transformation

    We deliberately avoid changing normal hyphens such as:

        state-of-the-art
    """

    if not text:
        return ""

    # Word-\nword -> wordword
    text = re.sub(
        r"(?<=[A-Za-zÄÖÜäöüß])-\n(?=[A-Za-zÄÖÜäöüß])",
        "",
        text,
    )

    return text


def clean_broken_spaces(text: str) -> str:
    """
    Fix common PDF extraction spacing problems.
    """

    if not text:
        return ""

    # Multiple spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around newlines.
    text = re.sub(
        r"[ \t]*\n[ \t]*",
        "\n",
        text,
    )

    return text


# ---------------------------------------------------------------------------
# Main text normalization
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize extracted CV text.

    Pipeline:

        1. Mojibake repair
        2. Unicode normalization
        3. Dash normalization
        4. PDF artefact removal
        5. Hyphenated-line repair
        6. Whitespace cleanup
        7. Blank-line cleanup
    """

    if not text:
        return ""

    # 1. Encoding repair.
    text = repair_mojibake(text)

    # 2. Unicode normalization.
    text = unicodedata.normalize("NFKC", text)

    # 3. Dash normalization.
    text = normalize_dashes(text)

    # 4. Non-breaking spaces.
    text = text.replace("\xa0", " ")

    # 5. Tabs.
    text = text.replace("\t", " ")

    # 6. Fix words split across PDF lines.
    text = fix_hyphenated_line_breaks(text)

    # 7. Remove obvious PDF artefact lines.
    text = remove_pdf_artifacts(text)

    # 8. Horizontal whitespace.
    text = clean_broken_spaces(text)

    # 9. Trim every line.
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            lines.append("")
            continue

        lines.append(line)

    text = "\n".join(lines)

    # 10. Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Single-line normalization
# ---------------------------------------------------------------------------

def normalize_line(line: str) -> str:
    """
    Normalize a single extracted PDF line.
    """

    if not line:
        return ""

    line = repair_mojibake(line)

    line = unicodedata.normalize(
        "NFKC",
        line,
    )

    line = normalize_dashes(line)

    line = line.replace("\xa0", " ")

    line = re.sub(
        r"\s+",
        " ",
        line,
    )

    return line.strip()
