# CV / Resume Extraction Pipeline

A generalized Python pipeline for extracting structured candidate information from CVs/resumes in **PDF format**.

The pipeline is designed for a realistic collection of CVs where:

* CV layouts and formatting vary significantly.
* Candidates may use different document structures.
* CVs can be written in **English or German**.
* Candidate names and backgrounds can vary.
* Information may appear in different orders or formats.
* PDF text extraction can introduce formatting and encoding artifacts.
* The same field may be represented in multiple ways.

The goal is to convert heterogeneous CV documents into a consistent structured representation suitable for further analysis, filtering, ranking, or export to CSV/XLSX/JSON.

---

## 1. Project Goals

The primary objective is to build a robust CV ingestion and extraction pipeline that can process approximately **100+ CVs** without requiring a custom parser for every individual document.

The pipeline should extract common candidate information such as:

* Personal information
* Education
* Professional experience
* Skills
* Languages
* Certifications
* Projects
* Additional sections

The extracted information should be normalized into a consistent schema.

### Supported CV languages

Currently the pipeline targets:

* English
* German

The pipeline should not assume that candidates themselves speak either language.

---

## 2. General Architecture

The pipeline follows a staged architecture:

```text
                    CV / Resume PDF
                           │
                           ▼
                 ┌───────────────────┐
                 │   PDF Extraction  │
                 │    / Docling      │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │  Text Cleaning &  │
                 │   Normalization   │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Section Detection │
                 └─────────┬─────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Education       Experience         Skills
          │                │                │
          ▼                ▼                ▼
       Extractor        Extractor        Extractor
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                 ┌───────────────────┐
                 │ Structured Record │
                 └─────────┬─────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
           JSON           CSV           XLSX
```

The important design principle is that **PDF extraction, section detection, and individual field extraction remain separate components**.

This makes individual extractors easier to improve without rewriting the entire pipeline.

---

# 3. Project Structure

Current project structure:

```text
student-corpus/
│
├── data/
│   ├── input/
│   │   └── *.pdf
│   │
│   ├── output/
│   │   ├── *.json
│   │   ├── *.csv
│   │   └── *.xlsx
│   │
│   └── intermediate/
│
├── src/
│   └── cv_pipeline/
│       │
│       ├── __init__.py
│       ├── pdf_extractor.py
│       ├── section_detector.py
│       ├── experience_extractor.py
│       ├── education_extractor.py
│       └── ...
│
├── test_experience.py
├── test_education.py
├── test_education_extractor.py
│
├── requirements.txt
├── README.md
└── ...
```

The project is intentionally modular.

---

# 4. Input

CV files are placed in:

```text
data/input/
```

Example:

```text
data/input/
├── Max_MustermannCV.pdf
└── Lebenslauf_MustermannMax.pdf
```

The filenames do not need to follow a specific naming convention.

The extractor should treat the filename as metadata rather than relying on it to determine the document structure.

---

# 5. PDF Extraction

The first stage converts the PDF into machine-readable text.

The PDF extractor is responsible only for extracting content from the document.

It should **not** attempt to determine whether a piece of text represents:

* Education
* Experience
* Skills
* Projects
* etc.

That responsibility belongs to later stages.

Example:

```python
from pathlib import Path
from src.cv_pipeline.pdf_extractor import extract_text

pdf_path = Path("data/input/example.pdf")

text = extract_text(pdf_path)

print(text)
```

---

# 6. Section Detection

After extracting text, the pipeline attempts to identify CV sections.

Typical section names include:

### English

```text
Experience
Professional Experience
Work Experience
Employment History
Education
Academic Background
Skills
Technical Skills
Languages
Projects
Certifications
```

### German

```text
Berufserfahrung
Beruflicher Werdegang
Berufliche Erfahrung
Ausbildung
Studium
Bildung
Kenntnisse
Fähigkeiten
Sprachkenntnisse
Projekte
Zertifikate
```

The section detector normalizes these different headings into common internal names.

For example:

```text
Berufserfahrung
Professional Experience
Work Experience
```

may all map to:

```text
experience
```

Similarly:

```text
Ausbildung
Education
Academic Background
```

may map to:

```text
education
```

Example:

```python
from src.cv_pipeline.section_detector import split_sections

sections = split_sections(text)

education = sections.get("education", "")
experience = sections.get("experience", "")
```

---

# 7. Education Extraction

Education is extracted independently from the rest of the CV.

The extractor aims to identify:

```text
institution
degree
field_of_study
grade
start_date
end_date
```

Example:

```python
{
    "institution": "RWTH Aachen University",
    "degree": "M.Sc",
    "field_of_study": "Computational Engineering Science",
    "grade": None,
    "start_date": "2024-10",
    "end_date": None
}
```

Another example:

```python
{
    "institution": "University Of Pune",
    "degree": "Bachelor of Engineering",
    "field_of_study": "Mechanical Engineering",
    "grade": "1.7",
    "start_date": "2022-08",
    "end_date": None
}
```

### Education normalization

The extractor should recognize different representations of degrees.

For example:

```text
Master of Science
M.Sc.
MSc
M. Sc.
```

can be normalized to:

```text
M.Sc
```

Likewise:

```text
Bachelor of Engineering
B.E.
BE
```

can be normalized to a common representation.

The exact normalization rules should remain centralized in the education extractor.

---

# 8. Grade Extraction

Grades are treated as an independent field.

Examples of possible formats include:

```text
GPA: 1.7
Grade: 1.7
Final grade: 1.7
GPA 3.8/4.0
Grade 2.1
```

The pipeline should not assume that all CVs use the same grading system.

Therefore the original grade representation should be preserved where possible.

Example:

```python
"grade": "1.7"
```

or:

```python
"grade": "3.8/4.0"
```

Future versions may add grade-system normalization, but extraction and normalization should remain separate concepts.

---

# 9. Experience Extraction

Professional experience is extracted into individual entries.

The target structure is:

```python
{
    "position": "...",
    "company": "...",
    "location": "...",
    "start_date": "...",
    "end_date": "...",
    "description": "...",
    "duration_years": ...
}
```

Example:

```python
{
    "position": "Operations Manager",
    "company": "Suyash Engineers and Automation Pvt. Ltd",
    "location": "Pune, India",
    "start_date": "2023-08",
    "end_date": "2025-01",
    "description": "...",
    "duration_years": 1.42
}
```

The extractor supports common date representations such as:

```text
08/2023 - 01/2025
08/2023 – 01/2025
2023-08 - 2025-01
August 2023 - January 2025
2023 - 2025
```

German CVs may also use:

```text
seit 10/2022
```

or similar ongoing-date expressions.

---

# 10. Date Normalization

Dates are normalized to:

```text
YYYY-MM
```

Examples:

```text
08/2023
```

becomes:

```text
2023-08
```

and:

```text
January 2025
```

becomes:

```text
2025-01
```

For ongoing positions:

```text
Present
Current
Ongoing
Now
seit
```

the extractor can represent the end date as the current month.

The internal normalized representation makes downstream processing easier.

---

# 11. Important Design Principle: Do Not Overfit to One CV

The pipeline is intended for heterogeneous CVs.

Therefore, extractors should **not** depend on fixed line numbers or one specific CV layout.

For example, this should be avoided:

```python
company = lines[5]
degree = lines[10]
```

because another CV may contain:

```text
Position
Company
Location
Date
Description
```

while another may contain:

```text
Date
Position
Company
Description
```

and another may use:

```text
Company
Position
Date
Location
```

Instead, extraction should combine:

* Date patterns
* Heading detection
* Known terminology
* Relative position of fields
* Language-specific keywords
* Formatting information where available
* Conservative heuristics

---

# 12. Handling English and German

The project currently targets two languages.

Language-specific terminology should therefore be centralized.

For example:

### Experience

```text
English:
Experience
Professional Experience
Work Experience
Internship
Working Student
Engineer
Manager

German:
Berufserfahrung
Berufliche Erfahrung
Praktikum
Werkstudent
Ingenieur
Mitarbeiter
```

### Education

```text
English:
Education
Bachelor
Master
University
Degree
GPA
Grade

German:
Ausbildung
Studium
Bachelor
Master
Universität
Note
Gesamtnote
```

The extractor should not require the CV language to be explicitly specified by the user.

---

# 13. PDF Encoding Problems

PDF text extraction can introduce encoding artifacts.

Examples observed during testing include:

```text
û
â€“
â€” 
\uf0b7
```

These can represent:

```text
–
—
•
```

or other characters that were incorrectly decoded.

Therefore, a normalization layer should be applied after PDF extraction.

Example transformations:

```text
â€“  -> –
â€”  -> —
\uf0b7 -> •
```

This should happen before section and field extraction whenever possible.

---

# 14. Candidate Diversity

The pipeline should not make assumptions about candidate nationality, name structure, or educational background.

Names may contain:

* Multiple family names
* Chinese names
* European names
* Middle names
* Initials
* Different ordering conventions

Similarly, universities and companies may be located anywhere in the world.

The extraction system should therefore treat names, institutions, and companies as **text entities**, rather than attempting to classify candidates based on nationality or name.

---

# 15. Extraction Philosophy

The pipeline follows three principles.

### 15.1 Extract first, normalize second

Do not immediately discard unusual information.

For example:

```text
GPA: 3.8/4.0
```

should first be extracted as:

```text
3.8/4.0
```

before any optional normalization.

---

### 15.2 Prefer missing values over incorrect values

If the extractor cannot confidently determine a company, grade, or field of study:

```python
None
```

is preferable to an incorrect value.

For example:

```python
{
    "company": None
}
```

is better than assigning a bullet point or description as the company.

---

### 15.3 Keep raw information available

The pipeline should ideally retain the original section text alongside normalized fields.

This makes debugging and improving extraction substantially easier.

A future structured record may therefore look like:

```python
{
    "candidate": {
        ...
    },

    "education": [
        ...
    ],

    "experience": [
        ...
    ],

    "skills": [
        ...
    ],

    "raw_sections": {
        "education": "...",
        "experience": "..."
    }
}
```

---

# 16. Testing Strategy

Testing is performed using several structurally different CVs rather than a single document.

Current test CVs include:

```text

```

These provide useful variation in:

* English vs German
* Date formats
* Education formats
* Experience layouts
* Bullet formatting
* Ongoing studies
* Grades
* Company/location ordering
* PDF encoding

Example test:

```powershell
python .\test_education_extractor.py
```

Example experience test:

```powershell
python .\test_experience.py
```

---

# 17. Development Workflow

When adding a new extractor, follow this workflow:

```text
1. Collect several real CV examples
             │
             ▼
2. Inspect extracted PDF text
             │
             ▼
3. Identify recurring patterns
             │
             ▼
4. Implement conservative extraction rules
             │
             ▼
5. Test against all existing CVs
             │
             ▼
6. Fix regressions
             │
             ▼
7. Add new edge-case tests
```

Do not optimize an extractor against only the CV currently being examined.

---

# 18. Current Extraction Modules

| Module                    | Purpose                            |
| ------------------------- | ---------------------------------- |
| `pdf_extractor.py`        | Convert PDF documents into text    |
| `section_detector.py`     | Identify and normalize CV sections |
| `experience_extractor.py` | Extract professional experience    |
| `education_extractor.py`  | Extract education information      |

Additional extractors can be added independently.

Potential future modules:

```text
skills_extractor.py
language_extractor.py
project_extractor.py
certification_extractor.py
personal_info_extractor.py
```

---

# 19. Output Schema

The final candidate record is intended to follow a stable schema.

Example:

```json
{
    "candidate": {
        "name": null,
        "email": null,
        "phone": null,
        "location": null
    },

    "education": [
        {
            "institution": "RWTH Aachen University",
            "degree": "M.Sc",
            "field_of_study": "Computational Engineering Science",
            "grade": null,
            "start_date": "2024-10",
            "end_date": null
        }
    ],

    "experience": [
        {
            "position": "Working Student",
            "company": "Example GmbH",
            "location": "Aachen, Germany",
            "start_date": "2023-11",
            "end_date": "2024-03",
            "description": null,
            "duration_years": 0.33
        }
    ],

    "skills": [],
    "languages": [],
    "certifications": [],
    "projects": []
}
```

Fields that cannot be reliably extracted should remain:

```python
None
```

or an empty list where appropriate.

---

# 20. Output Formats

The final pipeline is intended to support:

### JSON

Best for:

* Structured processing
* APIs
* Machine learning
* Debugging
* Preserving nested information

### CSV

Best for:

* Simple tabular analysis
* Excel
* Filtering candidates
* Data import

### XLSX

Best for:

* Human review
* Recruiter workflows
* Candidate comparison
* Manual corrections

A candidate may have multiple education or experience records, so the XLSX/CSV representation may eventually use either:

1. One row per candidate with serialized lists, or
2. Separate sheets/tables for candidates, education, experience, skills, etc.

The second approach is preferable once the pipeline grows.

---

# 21. Environment

The project is being developed in a Conda environment:

```text
student-corpus
```

Python version:

```text
Python 3.13
```

The environment contains the required PDF/document-processing dependencies.

Check the active environment with:

```powershell
conda env list
```

Check Python:

```powershell
python --version
```

Check installed packages:

```powershell
python -m pip check
```

---

# 22. Running the Pipeline

Activate the environment:

```powershell
conda activate student-corpus
```

Move to the project directory:

```powershell
cd "path\to\student-corpus"
```

Run an extractor test:

```powershell
python .\test_education_extractor.py
```

or:

```powershell
python .\test_experience.py
```

---

# 23. Debugging

When extraction produces an incorrect result, first inspect the raw extracted text.

For example:

```python
from pathlib import Path
from src.cv_pipeline.pdf_extractor import extract_text

text = extract_text(
    Path("data/input/example.pdf")
)

print(text)
```

Then inspect the relevant section:

```python
from src.cv_pipeline.section_detector import split_sections

sections = split_sections(text)

print(sections.get("education", ""))
```

This helps determine whether the problem is caused by:

```text
PDF extraction
       ↓
text normalization
       ↓
section detection
       ↓
field extraction
```

It is important to identify the stage responsible for an error before modifying an extractor.

---

# 24. Roadmap

The pipeline will be developed incrementally.

### Stage 1 — Document ingestion

* [x] PDF text extraction
* [x] Basic text normalization
* [x] Section detection

### Stage 2 — Core candidate information

* [ ] Personal information
* [x] Education
* [x] Grades
* [x] Experience
* [ ] Skills
* [ ] Languages

### Stage 3 — Additional CV information

* [ ] Projects
* [ ] Certifications
* [ ] Publications
* [ ] Awards
* [ ] Additional qualifications

### Stage 4 — Robustness

* [ ] More English CV formats
* [ ] More German CV formats
* [ ] Multi-column CV handling
* [ ] Better PDF encoding normalization
* [ ] Better date handling
* [ ] Improved company/location separation
* [ ] Improved degree normalization
* [ ] Regression test dataset

### Stage 5 — Batch processing

* [ ] Process 100+ CVs automatically
* [ ] Generate JSON output
* [ ] Generate CSV output
* [ ] Generate XLSX output
* [ ] Extraction error reporting
* [ ] Per-CV processing logs

---

# 25. Long-Term Design

The long-term goal is **not** to create a collection of special-case parsers.

Instead:

```text
100 CVs
   │
   ▼
One generalized ingestion pipeline
   │
   ├── PDF extraction
   ├── normalization
   ├── section detection
   ├── education extraction
   ├── experience extraction
   ├── skills extraction
   └── other extractors
   │
   ▼
One consistent candidate schema
   │
   ├── JSON
   ├── CSV
   └── XLSX
```

New CVs should primarily result in **new test cases and improvements to generalized rules**, rather than adding CV-specific code.

---

# 26. Guiding Principle

> **The pipeline should be robust to formatting differences, not dependent on formatting similarities.**

A CV parser that works perfectly on three CVs but fails on the fourth is not the final objective.

The objective is a system that can process a large and diverse CV corpus while:

* Extracting useful information consistently
* Preserving information when possible
* Avoiding fabricated values
* Handling English and German
* Handling different date formats
* Handling different CV layouts
* Providing predictable structured output
* Making extraction errors easy to diagnose and improve
