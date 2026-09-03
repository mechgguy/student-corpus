from pydantic import BaseModel, Field, field_validator


class Education(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    grade: str | None = None
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
    date_of_birth: str | None = None
    nationality: str | None = None
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

    @field_validator("technical_skills", mode="before")
    @classmethod
    def normalize_technical_skills(cls, value):
        """
        Ensure technical_skills always conforms to
        dict[str, list[str]].

        Empty/invalid extractor output should not
        cause the complete CV to fail.
        """

        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        # Some extractors may return [] when nothing
        # was found. Treat that as "no skills".
        if isinstance(value, list):
            return {}

        return {}

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
