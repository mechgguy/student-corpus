import src.cv_pipeline.education_extractor as e
from src.cv_pipeline.pdf_extractor import extract_text
from pathlib import Path


# =========================================================
# Input PDF
# =========================================================

pdf_path = Path(
    r"data/input/Job_CV_Template__DT___readingspace___software___Robotic_.pdf"
)


# =========================================================
# Extract PDF text
# =========================================================

text = extract_text(pdf_path)

start = text.find("Ausbildung")
end = text.find("Projekte")

if start == -1:
    raise RuntimeError("Could not find 'Ausbildung' section.")

section = text[start:end]

lines = e._normalize_lines(section)


# =========================================================
# Print normalized lines
# =========================================================

print("=" * 70)
print("EDUCATION SECTION")
print("=" * 70)

for i, line in enumerate(lines):
    print(f"{i:02d}: {line}")


# =========================================================
# Entry starts
# =========================================================

starts = e._find_entry_starts(lines)

print("\n" + "=" * 70)
print("ENTRY STARTS")
print("=" * 70)

print(starts)

for index in starts:
    print(
        f"{index:02d}: "
        f"{lines[index]}"
    )


# =========================================================
# Inspect each entry block
# =========================================================

print("\n" + "=" * 70)
print("ENTRY BLOCKS")
print("=" * 70)

for n, start_index in enumerate(starts):

    next_start = (
        starts[n + 1]
        if n + 1 < len(starts)
        else len(lines)
    )

    block_end = min(
        next_start,
        start_index + 8,
    )

    block = lines[
        start_index:block_end
    ]

    print("\n" + "-" * 70)
    print(
        f"ENTRY {n + 1}"
        f" | lines {start_index}:{block_end}"
    )
    print("-" * 70)

    for i, line in enumerate(
        block,
        start=start_index,
    ):
        print(
            f"{i:02d}: {line}"
        )

    # -----------------------------------------------------
    # Date
    # -----------------------------------------------------

    start_date, end_date = (
        e._find_date_near_entry(
            block,
            0,
            len(block),
        )
    )

    print(
        "\nDATE:"
    )
    print(
        f"  start_date = {start_date}"
    )
    print(
        f"  end_date   = {end_date}"
    )

    # -----------------------------------------------------
    # Candidate
    # -----------------------------------------------------

    candidate = e._build_candidate(
        block,
        start_date,
        end_date,
    )

    print(
        "\nCANDIDATE:"
    )

    if candidate:
        for key, value in candidate.items():
            print(
                f"  {key:15} = {value!r}"
            )
    else:
        print("  None")


# =========================================================
# Final extractor result
# =========================================================

print("\n" + "=" * 70)
print("FINAL extract_education() RESULT")
print("=" * 70)

result = e.extract_education(section)

for i, item in enumerate(result, 1):

    print(f"\nEDUCATION {i}")

    for key, value in item.items():
        print(
            f"  {key:15} = {value!r}"
        )
