from __future__ import annotations

from typing import Any


# ============================================================
# Generic helpers
# ============================================================

def _clean(value: Any) -> str:
    """
    Convert a value to a clean string.

    None / empty values become "".
    """
    if value is None:
        return ""

    value = str(value).strip()

    return value


def _format_date_range(
    start_date: Any,
    end_date: Any,
) -> str:
    """
    Format an experience date range.

    Examples:
        2022-01 – 2023-03
        2022-01 – Present
        2022-01
    """

    start = _clean(start_date)
    end = _clean(end_date)

    if start and end:
        return f"{start} – {end}"

    if start:
        return f"{start} – Present"

    if end:
        return f"Until {end}"

    return ""


# ============================================================
# Experience formatting
# ============================================================

def format_experience_entry(
    experience: dict[str, Any],
) -> str:
    """
    Convert one structured experience dictionary into a
    human-readable single-line representation.

    Input:

        {
            "company": "Bosch",
            "position": "Simulation Engineer Intern",
            "location": "Suzhou, China",
            "start_date": "2025-04",
            "end_date": "2025-07",
            "description": "...",
            "duration_years": 0.33
        }

    Output:

        2025-04 – 2025-07 | Simulation Engineer Intern | Bosch | Suzhou, China | ...
    """

    if not isinstance(experience, dict):
        return _clean(experience)

    parts = []

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    date_range = _format_date_range(
        experience.get("start_date"),
        experience.get("end_date"),
    )

    if date_range:
        parts.append(date_range)

    # --------------------------------------------------------
    # Position
    # --------------------------------------------------------

    position = _clean(
        experience.get("position")
    )

    if position:
        parts.append(position)

    # --------------------------------------------------------
    # Company
    # --------------------------------------------------------

    company = _clean(
        experience.get("company")
    )

    if company:
        parts.append(company)

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    location = _clean(
        experience.get("location")
    )

    if location:
        parts.append(location)

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    description = _clean(
        experience.get("description")
    )

    if description:
        parts.append(description)

    return " | ".join(parts)


def format_experience(
    experiences: Any,
) -> str:
    """
    Convert a list of structured experience dictionaries
    into a spreadsheet-friendly text value.

    One experience = one line.

    Example:

        2025-04 – 2025-07 | Simulation Engineer Intern | Bosch | Suzhou, China
        2024-01 – 2024-03 | Working Student | RWTH Aachen | Aachen, Germany
    """

    if not experiences:
        return ""

    # --------------------------------------------------------
    # Defensive handling
    # --------------------------------------------------------

    if isinstance(experiences, dict):
        experiences = [experiences]

    if not isinstance(experiences, (list, tuple)):
        return _clean(experiences)

    formatted = []

    for experience in experiences:

        if not isinstance(experience, dict):
            value = _clean(experience)

            if value:
                formatted.append(value)

            continue

        value = format_experience_entry(
            experience
        )

        if value:
            formatted.append(value)

    return "\n".join(formatted)


# ============================================================
# Education formatting
# ============================================================

def format_education_entry(
    education: dict[str, Any],
) -> str:
    """
    Convert one education dictionary into readable text.
    """

    if not isinstance(education, dict):
        return _clean(education)

    parts = []

    date_range = _format_date_range(
        education.get("start_date"),
        education.get("end_date"),
    )

    if date_range:
        parts.append(date_range)

    degree = _clean(
        education.get("degree")
    )

    field = _clean(
        education.get("field_of_study")
    )

    institution = _clean(
        education.get("institution")
    )

    grade = _clean(
        education.get("grade")
    )

    qualification = ""

    if degree and field:
        qualification = f"{degree} {field}"
    elif degree:
        qualification = degree
    elif field:
        qualification = field

    if qualification:
        parts.append(qualification)

    if institution:
        parts.append(institution)

    if grade:
        parts.append(f"Grade: {grade}")

    return " | ".join(parts)


def format_education(
    education: Any,
) -> str:
    """
    Convert structured education into spreadsheet-friendly text.
    """

    if not education:
        return ""

    if isinstance(education, dict):
        education = [education]

    if not isinstance(education, (list, tuple)):
        return _clean(education)

    formatted = []

    for item in education:

        value = format_education_entry(item)

        if value:
            formatted.append(value)

    return "\n".join(formatted)


# ============================================================
# Languages
# ============================================================

def format_languages(
    languages: Any,
) -> str:
    """
    Convert structured languages into readable text.

    Example:

        English: Fluent
        German: C1
        Chinese: Native
    """

    if not languages:
        return ""

    if isinstance(languages, dict):
        languages = [languages]

    if not isinstance(languages, (list, tuple)):
        return _clean(languages)

    formatted = []

    for language in languages:

        if not isinstance(language, dict):
            value = _clean(language)

            if value:
                formatted.append(value)

            continue

        name = _clean(
            language.get("language")
        )

        level = _clean(
            language.get("level")
        )

        if name and level:
            formatted.append(
                f"{name}: {level}"
            )

        elif name:
            formatted.append(name)

    return "\n".join(formatted)


# ============================================================
# Generic Candidate post-processing
# ============================================================

def format_candidate_for_export(
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a structured Candidate dictionary into a
    spreadsheet/export-friendly dictionary.

    IMPORTANT:
        This does NOT modify the original candidate.

    JSON should continue to use the original structured
    Candidate representation.
    """

    if not isinstance(candidate, dict):
        return candidate

    output = dict(candidate)

    # --------------------------------------------------------
    # Structured fields -> readable spreadsheet values
    # --------------------------------------------------------

    output["experience"] = format_experience(
        candidate.get("experience")
    )

    output["education"] = format_education(
        candidate.get("education")
    )

    output["languages"] = format_languages(
        candidate.get("languages")
    )

    # --------------------------------------------------------
    # Technical skills
    # --------------------------------------------------------

    technical_skills = candidate.get(
        "technical_skills"
    )

    if isinstance(technical_skills, dict):

        skill_lines = []

        for category, skills in technical_skills.items():

            if isinstance(skills, (list, tuple)):

                skills_text = ", ".join(
                    str(skill)
                    for skill in skills
                    if skill
                )

            else:
                skills_text = _clean(skills)

            if skills_text:
                skill_lines.append(
                    f"{category}: {skills_text}"
                )

        output["technical_skills"] = "\n".join(
            skill_lines
        )

    return output