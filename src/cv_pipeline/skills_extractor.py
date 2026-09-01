# skills_extractor.py

import json
import re
from pathlib import Path


ALIASES = {
    "python3": "Python",
    "python 3": "Python",
    "py": "Python",
    "matlab": "MATLAB",
    "siemens nx": "Siemens NX",
    "nx": "Siemens NX",
    "solid works": "SolidWorks",
    "ansys workbench": "ANSYS",
}


def load_skills():

    config_path = (
        Path(__file__).resolve()
        .parents[2]
        / "configs"
        / "skills.json"
    )

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_skill(skill: str):

    key = skill.lower().strip()

    return ALIASES.get(key, skill)


def extract_skills(section_text: str):

    if not section_text:
        return []

    skills = load_skills()

    results = {}

    for category, skill_list in skills.items():

        found = []

        for skill in skill_list:

            pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

            if re.search(
                pattern,
                section_text,
                re.IGNORECASE,
            ):

                normalized = normalize_skill(skill)

                if normalized not in found:
                    found.append(normalized)

        if found:
            results[category] = found

    return results
