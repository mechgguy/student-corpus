from __future__ import annotations

import pprint
from pathlib import Path

from src.cv_pipeline.post_processor import (
    format_experience,
    format_experience_entry,
    format_education,
    format_languages,
    format_candidate_for_export,
)
from src.cv_pipeline.cv_extractor import extract_cv
from src.cv_pipeline.pdf_extractor import extract_text
from src.cv_pipeline.text_normalizer import normalize_text
from src.cv_pipeline.section_detector import split_sections


PDF = Path(
    r"data\input\Job_CV_Template__Clean___Short___robotics___Paper_.pdf"
)


def separator(title: str):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ============================================================
# 1. Extract CV
# ============================================================

separator("POST-PROCESSING DEBUG")

print()
print("PDF:")
print(PDF)

if not PDF.exists():
    raise FileNotFoundError(
        f"PDF not found: {PDF}"
    )

separator("1. EXTRACTING CV")

raw_text = extract_text(PDF)

print(f"Raw characters: {len(raw_text):,}")
print(f"Raw lines:      {len(raw_text.splitlines()):,}")


# ============================================================
# 2. Run normal CV extractor
# ============================================================

separator("2. RUNNING CV EXTRACTOR")

candidate = extract_cv(raw_text)

print()
print("NAME:")
print(repr(candidate.get("name")))

print()
print("NATIONALITY:")
print(repr(candidate.get("nationality")))

print()
print("EXPERIENCE OBJECT TYPE:")
print(type(candidate.get("experience")).__name__)

experience = candidate.get("experience") or []

print()
print(f"EXPERIENCE ENTRIES: {len(experience)}")


# ============================================================
# 3. Show original structured experience
# ============================================================

separator("3. ORIGINAL STRUCTURED EXPERIENCE")

for i, item in enumerate(experience, start=1):

    print()
    print(f"EXPERIENCE #{i}")
    print("-" * 78)

    if isinstance(item, dict):

        for key in [
            "company",
            "position",
            "location",
            "start_date",
            "end_date",
            "description",
            "duration_years",
        ]:
            print(
                f"{key:20}: "
                f"{item.get(key)!r}"
            )

    else:

        print(
            "WARNING: experience entry is not a dictionary:"
        )

        pprint.pprint(item)


# ============================================================
# 4. Test individual experience formatter
# ============================================================

separator("4. FORMAT EACH EXPERIENCE ENTRY")

for i, item in enumerate(experience, start=1):

    print()
    print(f"EXPERIENCE #{i}")
    print("-" * 78)

    formatted = format_experience_entry(item)

    print(formatted)


# ============================================================
# 5. Final Excel-style experience output
# ============================================================

separator("5. FINAL FORMAT_EXPERIENCE() OUTPUT")

formatted_experience = format_experience(
    experience
)

print()
print(formatted_experience)


# ============================================================
# 6. Show repr so newlines are obvious
# ============================================================

separator("6. FORMAT_EXPERIENCE() REPR")

print(
    repr(formatted_experience)
)


# ============================================================
# 7. Test education
# ============================================================

separator("7. EDUCATION POST-PROCESSING")

education = candidate.get("education") or []

print()
print("Original education:")
pprint.pprint(education, width=120)

print()
print("Formatted education:")
print(format_education(education))


# ============================================================
# 8. Test languages
# ============================================================

separator("8. LANGUAGE POST-PROCESSING")

languages = candidate.get("languages") or []

print()
print("Original languages:")
pprint.pprint(languages, width=120)

print()
print("Formatted languages:")
print(format_languages(languages))


# ============================================================
# 9. Complete candidate conversion
# ============================================================

separator("9. COMPLETE EXCEL EXPORT OBJECT")

excel_candidate = format_candidate_for_export(
    candidate
)

print()

for key, value in excel_candidate.items():

    print()
    print(f"{key}")
    print("-" * 78)

    if isinstance(value, str):
        print(value)

    else:
        pprint.pprint(
            value,
            width=120,
        )


# ============================================================
# 10. Verify original candidate was NOT modified
# ============================================================

separator("10. STRUCTURED DATA INTEGRITY CHECK")

original_experience = candidate.get("experience")

print()
print(
    "Original experience is still a list:",
    isinstance(original_experience, list),
)

print(
    "Original experience contains dictionaries:",
    all(
        isinstance(x, dict)
        for x in original_experience
    ),
)

print()
print(
    "IMPORTANT:"
)
print(
    "The post-processor creates a separate export dictionary."
)
print(
    "The original structured candidate remains unchanged."
)


# ============================================================
# 11. Final summary
# ============================================================

separator("DEBUG SUMMARY")

print()
print(
    f"Experience entries:       {len(experience)}"
)

print(
    f"Formatted experience chars: "
    f"{len(formatted_experience):,}"
)

print(
    "Excel experience type:    ",
    type(
        excel_candidate.get("experience")
    ).__name__,
)

print(
    "Excel experience contains dictionaries:",
    isinstance(
        excel_candidate.get("experience"),
        (list, dict),
    ),
)

print()
print("POST-PROCESSING DEBUG COMPLETE")