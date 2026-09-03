from __future__ import annotations

from pathlib import Path
from pprint import pprint

from src.cv_pipeline.pdf_extractor import extract_text
from src.cv_pipeline.experience_extractor import (
    extract_experience,
    calculate_total_experience,
)
from src.cv_pipeline.text_normalizer import normalize_text
from src.cv_pipeline.section_detector import split_sections


# =========================================================
# CONFIGURATION
# =========================================================

PDF_PATH = Path(
    r"data/input/Job_CV_Template__Clean___Short___robotics___Paper_.pdf"
)


# =========================================================
# HELPERS
# =========================================================

def print_separator(title: str = ""):
    print()
    print("=" * 78)

    if title:
        print(title)

        print("=" * 78)


def print_section_text(title: str, text: str):
    print_separator(title)

    if not text:
        print("(EMPTY)")
        return

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):
        print(f"{index:03d}: {line!r}")


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 78)
    print("EXPERIENCE EXTRACTION DEBUG")
    print("=" * 78)

    print()
    print("PDF:")
    print(PDF_PATH)

    if not PDF_PATH.exists():
        print()
        print("ERROR: PDF does not exist.")
        return

    # -----------------------------------------------------
    # 1. Extract raw PDF text
    # -----------------------------------------------------

    print_separator("1. EXTRACTING PDF TEXT")

    raw_text = extract_text(PDF_PATH)

    print(f"Characters: {len(raw_text):,}")
    print(
        f"Lines: "
        f"{len(raw_text.splitlines()):,}"
    )

    # -----------------------------------------------------
    # 2. Normalize text
    # -----------------------------------------------------

    print_separator("2. NORMALIZED TEXT")

    text = normalize_text(raw_text)

    print(f"Characters: {len(text):,}")
    print(
        f"Lines: "
        f"{len(text.splitlines()):,}"
    )

    # -----------------------------------------------------
    # 3. Detect sections
    # -----------------------------------------------------

    sections = split_sections(text)

    print_separator("3. DETECTED SECTIONS")

    if not sections:
        print("(NO SECTIONS DETECTED)")
    else:
        for name, content in sections.items():

            if content:
                line_count = len(
                    [
                        x
                        for x in content.splitlines()
                        if x.strip()
                    ]
                )

                char_count = len(content)

                print(
                    f"{name:20s} "
                    f"{line_count:4d} lines "
                    f"{char_count:7d} chars"
                )

    # -----------------------------------------------------
    # 4. Find experience section
    # -----------------------------------------------------

    experience_text = sections.get(
        "experience",
        "",
    )

    print_section_text(
        "4. EXPERIENCE SECTION USED BY EXTRACTOR",
        experience_text,
    )

    # -----------------------------------------------------
    # 5. Run experience extractor
    # -----------------------------------------------------

    print_separator("5. EXTRACT_EXPERIENCE() RESULT")

    try:

        experience = extract_experience(
            experience_text
        )

    except Exception as exc:

        print()
        print("ERROR WHILE RUNNING extract_experience():")
        print(type(exc).__name__)
        print(str(exc))

        raise

    print()
    print(
        "Number of experience entries:",
        len(experience)
        if isinstance(experience, list)
        else "NOT A LIST",
    )

    # -----------------------------------------------------
    # 6. Pretty-print experience
    # -----------------------------------------------------

    print_separator("6. EXTRACTED EXPERIENCE")

    if not experience:

        print("(NO EXPERIENCE FOUND)")

    elif isinstance(experience, list):

        for index, item in enumerate(experience, start=1):

            print()
            print("-" * 78)
            print(f"EXPERIENCE #{index}")
            print("-" * 78)

            if isinstance(item, dict):

                for key, value in item.items():

                    print(
                        f"{key:30s}: {value!r}"
                    )

            else:

                print(repr(item))

    else:

        pprint(experience)

    # -----------------------------------------------------
    # 7. Calculate total experience
    # -----------------------------------------------------

    print_separator("7. TOTAL EXPERIENCE")

    try:

        total = calculate_total_experience(
            experience
        )

        print(
            "Total experience:",
            repr(total),
        )

    except Exception as exc:

        print()
        print(
            "ERROR WHILE CALCULATING "
            "TOTAL EXPERIENCE:"
        )

        print(
            type(exc).__name__,
            str(exc),
        )

    # -----------------------------------------------------
    # 8. Print all date-like lines
    #
    # Useful for debugging German/English
    # date formats.
    # -----------------------------------------------------

    print_separator(
        "8. DATE-LIKE LINES IN EXPERIENCE SECTION"
    )

    import re

    date_pattern = re.compile(
        r"""
        (?:
            \b
            (?:19|20)\d{2}
            \b
        )
        |
        (?:
            \b
            \d{1,2}
            [./-]
            \d{1,2}
            [./-]
            (?:19|20)?\d{2}
            \b
        )
        |
        (?:
            \b
            \d{1,2}
            [./-]
            (?:19|20)\d{2}
            \b
        )
        |
        (?:
            \b
            (?:
                jan(?:uary)?
                |feb(?:ruary)?
                |märz
                |maerz
                |march
                |apr(?:il)?
                |may
                |mai
                |jun(?:e|i)?
                |jul(?:y|i)?
                |aug(?:ust)?
                |sep(?:tember)?
                |sept(?:ember)?
                |okt(?:ober)?
                |oct(?:ober)?
                |nov(?:ember)?
                |dez(?:ember)?
                |dec(?:ember)?
            )
            \b
            [\s-]?
            (?:19|20)?\d{2}
        )
        |
        (?:
            \b
            (?:19|20)\d{2}
            [\s-]
            (?:
                jan(?:uary)?
                |feb(?:ruary)?
                |märz
                |maerz
                |march
                |apr(?:il)?
                |may
                |mai
                |jun(?:e|i)?
                |jul(?:y|i)?
                |aug(?:ust)?
                |sep(?:tember)?
                |sept(?:ember)?
                |okt(?:ober)?
                |oct(?:ober)?
                |nov(?:ember)?
                |dez(?:ember)?
                |dec(?:ember)?
            )
            \b
        )
        |
        (?:
            \b
            (?:present|heute|aktuell|laufend)
            \b
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    found_dates = []

    for line in experience_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if date_pattern.search(line):
            found_dates.append(line)

    if found_dates:

        for index, line in enumerate(
            found_dates,
            start=1,
        ):
            print(
                f"{index:03d}: {line!r}"
            )

    else:

        print("(NO DATE-LIKE LINES FOUND)")

    # -----------------------------------------------------
    # 9. Print raw experience lines
    #
    # This is particularly useful for finding cases where
    # PDF extraction has split dates/company names across
    # multiple lines.
    # -----------------------------------------------------

    print_separator(
        "9. RAW EXPERIENCE LINES"
    )

    experience_lines = [
        line.strip()
        for line in experience_text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(
        experience_lines
    ):

        print(
            f"{index:03d}: {line!r}"
        )

    # -----------------------------------------------------
    # 10. Full extraction
    # -----------------------------------------------------

    print_separator(
        "10. FULL EXPERIENCE PIPELINE CHECK"
    )

    try:

        from src.cv_pipeline.cv_extractor import (
            extract_cv,
        )

        result = extract_cv(
            raw_text
        )

        print()
        print(
            "NAME:",
            repr(result.get("name")),
        )

        print(
            "NATIONALITY:",
            repr(result.get("nationality")),
        )

        print(
            "TOTAL EXPERIENCE:",
            repr(
                result.get(
                    "total_experience_years"
                )
            ),
        )

        print()

        print(
            "EXPERIENCE FROM FULL PIPELINE:"
        )

        pprint(
            result.get("experience")
        )

    except Exception as exc:

        print()
        print(
            "ERROR IN FULL CV PIPELINE:"
        )

        print(
            type(exc).__name__,
            str(exc),
        )

    # -----------------------------------------------------
    # Finished
    # -----------------------------------------------------

    print()
    print("=" * 78)
    print("DEBUG COMPLETE")
    print("=" * 78)


if __name__ == "__main__":
    main()