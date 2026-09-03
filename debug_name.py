from pathlib import Path
import inspect

import src.cv_pipeline.cv_extractor as cv
from src.cv_pipeline.pdf_extractor import extract_text


PDF = Path(
    r"data/input/Job_CV_Template__Clean___Short___robotics___Paper_.pdf"
)


print("=" * 70)
print("NAME DETECTOR DEBUG")
print("=" * 70)

print("\nCV EXTRACTOR:")
print(cv.__file__)

print("\nNAME-RELATED FUNCTIONS / VARIABLES:")
for x in sorted(dir(cv)):
    if "name" in x.lower():
        print(" ", x)

# ---------------------------------------------------------
# Extract PDF text
# ---------------------------------------------------------

text = extract_text(PDF)

if not text:
    raise RuntimeError("No text extracted from PDF.")

lines = [
    line.strip()
    for line in text.splitlines()
    if line.strip()
]

# ---------------------------------------------------------
# Show beginning of CV
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FIRST 80 LINES OF PDF TEXT")
print("=" * 70)

for i, line in enumerate(lines[:80]):
    print(f"{i:02d}: {line!r}")

# ---------------------------------------------------------
# Test internal name scoring if available
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("NAME CANDIDATE SCORING")
print("=" * 70)

if hasattr(cv, "_name_score"):

    print("\nCandidates considered from first 25 lines:\n")

    scored = []

    for index, line in enumerate(lines[:25]):

        try:
            score = cv._name_score(line, index)
        except Exception as exc:
            print(f"ERROR scoring line {index}: {exc}")
            continue

        if score > 0:
            scored.append(
                (
                    score,
                    index,
                    line,
                )
            )

    scored.sort(
        key=lambda x: (
            -x[0],
            x[1],
        )
    )

    for score, index, line in scored:
        print(
            f"score={score:>3} | "
            f"line={index:02d} | "
            f"{line!r}"
        )

else:
    print("_name_score() is not available.")

# ---------------------------------------------------------
# Test _looks_like_name if available
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("NAME-LIKE TEST")
print("=" * 70)

if hasattr(cv, "_looks_like_name"):

    for index, line in enumerate(lines[:25]):

        try:
            result = cv._looks_like_name(line)
        except Exception as exc:
            print(
                f"line={index:02d} "
                f"{line!r} -> ERROR: {exc}"
            )
            continue

        print(
            f"line={index:02d} "
            f"{line!r:45} -> {result}"
        )

else:
    print("_looks_like_name() is not available.")

# ---------------------------------------------------------
# Actual extraction
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("ACTUAL EXTRACT_NAME() RESULT")
print("=" * 70)

name = cv.extract_name(text)

print("\nEXTRACTED NAME:")
print(repr(name))

# ---------------------------------------------------------
# Full CV extraction
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FULL CV EXTRACTION")
print("=" * 70)

if hasattr(cv, "extract_cv"):

    candidate = cv.extract_cv(text)

    print("\nEXTRACTED NAME:")
    print(repr(candidate.get("name")))

    print("\nEXTRACTED NATIONALITY:")
    print(repr(candidate.get("nationality")))

else:
    print("extract_cv() is not available.")

print("\n" + "=" * 70)
print("DEBUG COMPLETE")
print("=" * 70)