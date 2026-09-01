import json
from pathlib import Path

import pandas as pd

from .schemas import Candidate


def candidates_to_records(
    candidates: list[Candidate],
) -> list[dict]:

    return [
        candidate.model_dump()
        for candidate in candidates
    ]


def save_json(
    candidates: list[Candidate],
    path: Path,
):

    records = candidates_to_records(candidates)

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


def save_csv(
    candidates: list[Candidate],
    path: Path,
):

    records = candidates_to_records(candidates)

    dataframe = pd.DataFrame(records)

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
    )


def save_xlsx(
    candidates: list[Candidate],
    path: Path,
):

    records = candidates_to_records(candidates)

    dataframe = pd.DataFrame(records)

    dataframe.to_excel(
        path,
        index=False,
    )
