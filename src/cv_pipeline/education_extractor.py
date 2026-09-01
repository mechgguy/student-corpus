# education_extractor.py

import re


DEGREE_PATTERNS = [
    r"\bB\.?Sc\.?\b",
    r"\bM\.?Sc\.?\b",
    r"\bB\.?Eng\.?\b",
    r"\bM\.?Eng\.?\b",
    r"\bB\.?Tech\.?\b",
    r"\bM\.?Tech\.?\b",
    r"\bB\.?E\.?\b",
    r"\bM\.?E\.?\b",
    r"\bMBA\b",
    r"\bPh\.?D\.?\b",
    r"\bBachelor\b",
    r"\bMaster\b",
    r"\bDoctorate\b",
    r"\bDiploma\b",
]


DATE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b"
)


def find_degree(line: str):

    for pattern in DEGREE_PATTERNS:

        match = re.search(
            pattern,
            line,
            re.IGNORECASE,
        )

        if match:
            return match.group(0)

    return None


def extract_education(section_text: str):

    if not section_text:
        return []

    lines = [
        line.strip()
        for line in section_text.splitlines()
        if line.strip()
    ]

    results = []

    for i, line in enumerate(lines):

        degree = find_degree(line)

        if not degree:
            continue

        start_year = None
        end_year = None

        # Search current and nearby lines
        context = "\n".join(
            lines[max(0, i - 1): min(len(lines), i + 3)]
        )

        years = DATE_PATTERN.findall(context)

        if len(years) >= 2:

            start_year = years[0]
            end_year = years[1]

        elif len(years) == 1:

            end_year = years[0]

        institution = None

        # Often institution appears immediately before degree
        if i > 0:
            institution = lines[i - 1]

        results.append(
            {
                "institution": institution,
                "degree": degree,
                "field_of_study": None,
                "start_year": start_year,
                "end_year": end_year,
            }
        )

    return results
