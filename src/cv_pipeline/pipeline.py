from pathlib import Path
from uuid import uuid4

from .pdf_extractor import extract_text
from .cv_extractor import extract_candidate
from .validator import validate_candidate
from .schemas import Candidate


def process_pdf(pdf_path: Path) -> Candidate:

    text = extract_text(pdf_path)

    if not text:
        raise ValueError(
            f"No text extracted from {pdf_path.name}"
        )

    candidate = extract_candidate(
        text=text,
        candidate_id=str(uuid4()),
        filename=pdf_path.name,
    )

    return validate_candidate(candidate)


def process_directory(
    input_dir: Path,
):

    candidates = []
    failures = []

    pdf_files = sorted(
        input_dir.glob("*.pdf")
    )

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_path in pdf_files:

        print(f"Processing: {pdf_path.name}")

        try:

            candidate = process_pdf(pdf_path)

            candidates.append(candidate)

            print(
                f"  OK: {candidate.name or 'Unknown name'}"
            )

        except Exception as error:

            print(f"  FAILED: {error}")

            failures.append(
                {
                    "filename": pdf_path.name,
                    "error": str(error),
                }
            )

    return candidates, failures
