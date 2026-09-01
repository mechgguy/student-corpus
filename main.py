import json
from pathlib import Path

from src.cv_pipeline.pipeline import process_directory
from src.cv_pipeline.output import (
    save_json,
    save_csv,
    save_xlsx,
)


BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"
FAILED_DIR = BASE_DIR / "data" / "failed"


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FAILED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates, failures = process_directory(
        INPUT_DIR
    )

    if candidates:

        save_json(
            candidates,
            OUTPUT_DIR / "candidates.json",
        )

        save_csv(
            candidates,
            OUTPUT_DIR / "candidates.csv",
        )

        save_xlsx(
            candidates,
            OUTPUT_DIR / "candidates.xlsx",
        )

    if failures:

        with (
            FAILED_DIR / "failed.json"
        ).open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                failures,
                file,
                indent=2,
                ensure_ascii=False,
            )

    print()
    print("=" * 60)
    print(
        f"Processed: {len(candidates)}"
    )
    print(
        f"Failed:    {len(failures)}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
