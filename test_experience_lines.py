from pathlib import Path

from src.cv_pipeline.pdf_extractor import extract_text
from src.cv_pipeline.section_detector import split_sections


FILES = [
    "Adrien_CV.pdf",
    "Atharva. D_CV (1).pdf",
    "Lebenslauf_Shaozhuo_Liu Johnson Electric.pdf",
]


for filename in FILES:

    print()
    print("=" * 80)
    print(filename)
    print("=" * 80)

    path = Path("data/input") / filename

    text = extract_text(path)
    sections = split_sections(text)

    experience = sections.get("experience", "")

    for i, line in enumerate(experience.splitlines()):
        print(f"{i:03d}: {line!r}")
