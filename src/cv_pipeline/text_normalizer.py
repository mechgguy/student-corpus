import re


def normalize_text(text: str) -> str:

    # Normalize different dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("−", "-")

    # Normalize non-breaking spaces
    text = text.replace("\xa0", " ")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_line(line: str) -> str:

    line = line.strip()

    line = re.sub(r"\s+", " ", line)

    return line
