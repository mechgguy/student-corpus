from .schemas import Candidate


def validate_candidate(candidate: Candidate) -> Candidate:

    if candidate.email:
        candidate.email = candidate.email.lower().strip()

    if candidate.linkedin:
        candidate.linkedin = candidate.linkedin.strip()

    if candidate.github:
        candidate.github = candidate.github.strip()

    if candidate.name:
        candidate.name = " ".join(
            candidate.name.split()
        )

    return candidate
