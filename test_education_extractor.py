from pathlib import Path

from src.cv_pipeline.pdf_extractor import extract_text
from src.cv_pipeline.section_detector import split_sections
from src.cv_pipeline.education_extractor import extract_education


FILES = [
    "Adrien_CV.pdf",
    "Atharva. D_CV (1).pdf",
    "Lebenslauf_Shaozhuo_Liu Johnson Electric.pdf",
    "Zhichao Wen CV Business Development.pdf",
    ]


for filename in FILES:

    print("\n" + "=" * 80)
    print(filename)
    print("=" * 80)

    path = Path("data/input") / filename

    text = extract_text(path)
    sections = split_sections(text)

    education = sections.get("education", "")

    results = extract_education(education)

    for result in results:
        print(result)
