from pathlib import Path

from src.cv_pipeline.pdf_extractor import extract_text
from src.cv_pipeline.section_detector import split_sections
from src.cv_pipeline.experience_extractor import (
    extract_experience,
    calculate_total_experience,
)


FILES = [
    "Adrien_CV.pdf",
    "Atharva. D_CV (1).pdf",
    "Lebenslauf_Shaozhuo_Liu Johnson Electric.pdf",
]


for filename in FILES:

    print()
    print("=" * 70)
    print(filename)
    print("=" * 70)

    path = Path("data/input") / filename

    text = extract_text(path)
    sections = split_sections(text)

    experience_text = sections.get("experience", "")

    experiences = extract_experience(experience_text)

    for experience in experiences:
        print(experience)

    print()
    print("TOTAL:", calculate_total_experience(experiences))

