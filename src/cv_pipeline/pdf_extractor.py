from pathlib import Path

import pymupdf


def extract_text(pdf_path: str | Path) -> str:

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF: {pdf_path}")

    pages = []

    with pymupdf.open(pdf_path) as document:

        for page in document:
            text = page.get_text("text")

            if text:
                pages.append(text)

    return "\n".join(pages).strip()
