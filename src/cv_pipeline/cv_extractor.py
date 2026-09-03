from __future__ import annotations

from src.cv_pipeline.personal_extractor import (
    extract_name,
    extract_nationality,
)
from .contact_extractor import extract_contacts
from .location_extractor import extract_location
from .language_extractor import extract_languages
from .skills_extractor import extract_skills
from .experience_extractor import (
    extract_experience,
    calculate_total_experience,
)
from .education_extractor import extract_education
from .text_normalizer import normalize_text
from .section_detector import split_sections
from .schemas import Candidate


def extract_candidate(
    text: str,
    candidate_id: str,
    filename: str,
) -> Candidate:
    """
    Extract structured candidate information from CV text.

    Pipeline:
        raw text
            ↓
        normalize text
            ↓
        detect sections
            ↓
        specialized extractors
            ↓
        Candidate Pydantic model
    """

    if not text or not text.strip():
        raise ValueError("CV text is empty.")

    # ---------------------------------------------------------
    # 1. Normalize text
    # ---------------------------------------------------------

    text = normalize_text(text)

    # ---------------------------------------------------------
    # 2. Detect CV sections
    # ---------------------------------------------------------

    sections = split_sections(text)

    # ---------------------------------------------------------
    # 3. Contact information
    # ---------------------------------------------------------

    header_text = sections.get("header", text)

    contacts = extract_contacts(header_text)

    # ---------------------------------------------------------
    # 4. Location
    # ---------------------------------------------------------

    location = extract_location(header_text)

    # ---------------------------------------------------------
    # 5. Languages
    # ---------------------------------------------------------

    language_text = "\n".join(
        filter(
            None,
            [
                sections.get("languages", ""),
                sections.get("skills", ""),
            ],
        )
    )

    languages = extract_languages(
        language_text
    )

    # ---------------------------------------------------------
    # 6. Skills
    # ---------------------------------------------------------

    skills = extract_skills(
        sections.get("skills", "")
    )

    if not isinstance(skills, dict):
        skills = {}

    # ---------------------------------------------------------
    # 7. Work experience
    # ---------------------------------------------------------

    experience = extract_experience(
        sections.get("experience", "")
    )

    total_experience = calculate_total_experience(
        experience
    )

    # ---------------------------------------------------------
    # 8. Education
    # ---------------------------------------------------------

    education = extract_education(
        sections.get("education", "")
    )

    # ---------------------------------------------------------
    # 9. Summary
    # ---------------------------------------------------------

    summary = sections.get("summary")

    # ---------------------------------------------------------
    # 10. Build Candidate model
    # ---------------------------------------------------------

    candidate = Candidate(
        candidate_id=candidate_id,
        filename=filename,

        # name=contacts.get("name"),
        name = extract_name(text),
        date_of_birth=contacts.get("date_of_birth"),
        nationality = extract_nationality(text),
        email=contacts.get("email"),
        phone=contacts.get("phone"),

        location=location,

        linkedin=contacts.get("linkedin"),
        github=contacts.get("github"),

        summary=summary,

        education=education,
        experience=experience,

        total_experience_years=total_experience,
        technical_skills=skills or {},
        software_skills=[],

        languages=languages,

        certifications=[],
        projects=[],

        raw_text=text,
    )

    # Add calculated experience if supported by schema.
    #
    # Currently Candidate does not contain
    # total_experience_years, so the value is calculated
    # above but is not added to the Pydantic model.
    #
    # This can be added to schemas.py later.

    return candidate


# -------------------------------------------------------------
# Backwards-compatible alias
# -------------------------------------------------------------
#
# If other code still calls extract_cv(), it will continue
# to work.
#

def extract_cv(text: str):
    """
    Backwards-compatible low-level extraction function.

    This is useful for debugging the individual extractors.
    """

    text = normalize_text(text)

    sections = split_sections(text)

    header_text = sections.get("header", text)

    contacts = extract_contacts(header_text)

    location = extract_location(header_text)

    language_text = "\n".join(
        filter(
            None,
            [
                sections.get("languages", ""),
                sections.get("skills", ""),
            ],
        )
    )
    
    languages = extract_languages(
        language_text
    )
    
    skills = extract_skills(
        sections.get("skills", "")
    )

    experience = extract_experience(
        sections.get("experience", "")
    )

    education = extract_education(
        sections.get("education", "")
    )

    total_experience = calculate_total_experience(
        experience
    )

    return {
        # "name": contacts.get("name"),
        "name": extract_name(text),
        "date_of_birth": contacts.get("date_of_birth"),
        "nationality": extract_nationality(text),
        "email": contacts.get("email"),
        "phone": contacts.get("phone"),
        "location": location,

        "linkedin": contacts.get("linkedin"),
        "github": contacts.get("github"),

        "education": education,
        "experience": experience,

        "total_experience_years": total_experience,

        "technical_skills": skills,
        "software_skills": [],

        "languages": languages,

        "summary": sections.get("summary"),

        "raw_text": text,
    }


