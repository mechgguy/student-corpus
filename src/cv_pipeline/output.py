from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .schemas import Candidate
from .post_processor import format_candidate_for_export


# ============================================================
# Structured records
# ============================================================

def candidates_to_records(
    candidates: list[Candidate],
) -> list[dict]:
    """
    Convert Candidate models to dictionaries.

    This preserves the original structured representation.

    Used for JSON export.
    """

    return [
        candidate.model_dump()
        for candidate in candidates
    ]


# ============================================================
# Export-friendly records
# ============================================================

def candidates_to_export_records(
    candidates: list[Candidate],
) -> list[dict]:
    """
    Convert Candidate models into export-friendly dictionaries.

    Structured fields such as:

        experience
        education
        languages
        technical_skills

    are converted into readable strings.

    The original Candidate objects are NOT modified.
    """

    records = []

    for candidate in candidates:

        structured = candidate.model_dump()

        export_record = format_candidate_for_export(
            structured
        )

        records.append(
            export_record
        )

    return records


# ============================================================
# JSON
# ============================================================

def save_json(
    candidates: list[Candidate],
    path: Path,
):
    """
    Save candidates as structured JSON.

    IMPORTANT:
        JSON keeps the original structured representation.

    For example:

        "experience": [
            {
                "company": "Bosch",
                "position": "Engineer",
                ...
            }
        ]

    """

    records = candidates_to_records(
        candidates
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# CSV
# ============================================================

def save_csv(
    candidates: list[Candidate],
    path: Path,
):
    """
    Save candidates as CSV.

    Structured fields are converted to readable strings
    using the post-processing module.
    """

    records = candidates_to_export_records(
        candidates
    )

    dataframe = pd.DataFrame(
        records
    )

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
    )


# ============================================================
# XLSX
# ============================================================

def save_xlsx(
    candidates: list[Candidate],
    path: Path,
):
    """
    Save candidates as Excel.

    Structured fields are converted to readable strings
    using the post-processing module.
    """

    records = candidates_to_export_records(
        candidates
    )

    dataframe = pd.DataFrame(
        records
    )

    dataframe.to_excel(
        path,
        index=False,
    )