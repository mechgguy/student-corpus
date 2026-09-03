from __future__ import annotations

from src.cv_pipeline.personal_extractor import (
    extract_name,
    extract_name_from_filename,
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


# =========================================================
# Candidate extraction
# =========================================================

def extract_candidate(
    text: str,
    candidate_id: str,
    filename: str,
) -> Candidate:
    """
    Extract structured candidate information from CV text.

    Name detection priority:

        1. Filename
        2. Explicit name field inside CV
        3. Name candidates detected from CV text

    Filename examples:

        Max_Mustermann_CV.pdf
        Anna-Schmidt_Resume.pdf

    If the filename does not contain a reliable name,
    the extractor automatically falls back to the CV text.
    """

    if not text or not text.strip():
        raise ValueError(
            "CV text is empty."
        )

    # -----------------------------------------------------
    # 1. Normalize text
    # -----------------------------------------------------

    text = normalize_text(text)

    # -----------------------------------------------------
    # 2. Detect sections
    # -----------------------------------------------------

    sections = split_sections(text)

    # -----------------------------------------------------
    # 3. Contact information
    # -----------------------------------------------------

    header_text = sections.get(
        "header",
        text,
    )

    contacts = extract_contacts(
        header_text
    )

    # -----------------------------------------------------
    # 4. Personal information
    # -----------------------------------------------------

    # FIRST: filename
    name = extract_name_from_filename(
        filename
    )

    # FALLBACK: CV text
    if not name:
        name = extract_name(text)

    nationality = extract_nationality(
        text
    )

    # -----------------------------------------------------
    # 5. Location
    # -----------------------------------------------------

    location = extract_location(
        header_text
    )

    # -----------------------------------------------------
    # 6. Languages
    # -----------------------------------------------------

    language_text = "\n".join(
        filter(
            None,
            [
                sections.get(
                    "languages",
                    "",
                ),
                sections.get(
                    "skills",
                    "",
                ),
            ],
        )
    )

    languages = extract_languages(
        language_text
    )

    # -----------------------------------------------------
    # 7. Skills
    # -----------------------------------------------------

    skills = extract_skills(
        sections.get(
            "skills",
            "",
        )
    )

    if not isinstance(skills, dict):
        skills = {}

    # -----------------------------------------------------
    # 8. Work experience
    # -----------------------------------------------------

    experience = extract_experience(
        sections.get(
            "experience",
            "",
        )
    )

    total_experience = (
        calculate_total_experience(
            experience
        )
    )

    # -----------------------------------------------------
    # 9. Education
    # -----------------------------------------------------

    education = extract_education(
        sections.get(
            "education",
            "",
        )
    )

    # -----------------------------------------------------
    # 10. Summary
    # -----------------------------------------------------

    summary = sections.get(
        "summary"
    )

    # -----------------------------------------------------
    # 11. Candidate model
    # -----------------------------------------------------

    candidate = Candidate(
        candidate_id=candidate_id,
        filename=filename,

        name=name,

        date_of_birth=contacts.get(
            "date_of_birth"
        ),

        nationality=nationality,

        email=contacts.get(
            "email"
        ),

        phone=contacts.get(
            "phone"
        ),

        location=location,

        linkedin=contacts.get(
            "linkedin"
        ),

        github=contacts.get(
            "github"
        ),

        summary=summary,

        education=education,

        experience=experience,

        total_experience_years=(
            total_experience
        ),

        technical_skills=(
            skills or {}
        ),

        software_skills=[],

        languages=languages,

        certifications=[],

        projects=[],

        raw_text=text,
    )

    return candidate


# =========================================================
# Backwards-compatible extraction
# =========================================================

def extract_cv(
    text: str,
    filename: str | None = None,
):
    """
    Backwards-compatible low-level extraction.

    If filename is supplied:

        filename -> CV name -> result

    Otherwise:

        CV text -> result
    """

    if not text or not text.strip():
        raise ValueError(
            "CV text is empty."
        )

    # -----------------------------------------------------
    # Normalize
    # -----------------------------------------------------

    text = normalize_text(text)

    # -----------------------------------------------------
    # Sections
    # -----------------------------------------------------

    sections = split_sections(text)

    # -----------------------------------------------------
    # Contact information
    # -----------------------------------------------------

    header_text = sections.get(
        "header",
        text,
    )

    contacts = extract_contacts(
        header_text
    )

    # -----------------------------------------------------
    # Personal information
    # -----------------------------------------------------

    # Filename gets priority when available.
    name = None

    if filename:
        name = extract_name_from_filename(
            filename
        )

    # Fallback to CV text.
    if not name:
        name = extract_name(text)

    nationality = extract_nationality(
        text
    )

    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------

    location = extract_location(
        header_text
    )

    # -----------------------------------------------------
    # Languages
    # -----------------------------------------------------

    language_text = "\n".join(
        filter(
            None,
            [
                sections.get(
                    "languages",
                    "",
                ),
                sections.get(
                    "skills",
                    "",
                ),
            ],
        )
    )

    languages = extract_languages(
        language_text
    )

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    skills = extract_skills(
        sections.get(
            "skills",
            "",
        )
    )

    if not isinstance(skills, dict):
        skills = {}

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------

    experience = extract_experience(
        sections.get(
            "experience",
            "",
        )
    )

    total_experience = (
        calculate_total_experience(
            experience
        )
    )

    # -----------------------------------------------------
    # Education
    # -----------------------------------------------------

    education = extract_education(
        sections.get(
            "education",
            "",
        )
    )

    # -----------------------------------------------------
    # Return dictionary
    # -----------------------------------------------------

    return {
        "name": name,

        "date_of_birth": contacts.get(
            "date_of_birth"
        ),

        "nationality": nationality,

        "email": contacts.get(
            "email"
        ),

        "phone": contacts.get(
            "phone"
        ),

        "location": location,

        "linkedin": contacts.get(
            "linkedin"
        ),

        "github": contacts.get(
            "github"
        ),

        "education": education,

        "experience": experience,

        "total_experience_years": (
            total_experience
        ),

        "technical_skills": skills,

        "software_skills": [],

        "languages": languages,

        "summary": sections.get(
            "summary"
        ),

        "raw_text": text,
    }