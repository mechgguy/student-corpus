from pydantic import BaseModel, Field


class Education(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class Experience(BaseModel):
    company: str | None = None
    position: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    duration_years: float | None = None


class Language(BaseModel):
    language: str
    level: str | None = None


class Candidate(BaseModel):
    candidate_id: str
    filename: str

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    linkedin: str | None = None
    github: str | None = None

    summary: str | None = None

    education: list[Education] = Field(
        default_factory=list
    )

    experience: list[Experience] = Field(
        default_factory=list
    )

    total_experience_years: float | None = None

    technical_skills: dict[str, list[str]] = Field(
        default_factory=dict
    )

    software_skills: list[str] = Field(
        default_factory=list
    )

    languages: list[Language] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    projects: list[str] = Field(
        default_factory=list
    )

    raw_text: str | None = None
