from pathlib import Path

from src.cv_pipeline.pdf_extractor import extract_text
from src.cv_pipeline.cv_extractor import extract_cv


pdf = Path("data/input/test.pdf")

text = extract_text(pdf)

candidate = extract_cv(text)

print("\nNAME:")
print(candidate["name"])

print("\nEMAIL:")
print(candidate["email"])

print("\nPHONE:")
print(candidate["phone"])

print("\nLOCATION:")
print(candidate["location"])

print("\nLINKEDIN:")
print(candidate["linkedin"])

print("\nLANGUAGES:")
print(candidate["languages"])

print("\nSKILLS:")
print(candidate["technical_skills"])

print("\nEDUCATION:")
print(candidate["education"])

print("\nEXPERIENCE:")
for job in candidate["experience"]:
    print(job)

print("\nTOTAL EXPERIENCE:")
print(candidate["total_experience_years"])
