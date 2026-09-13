"""
Module 2: Resume Score Analyzer
---------------------------------
Analyzes resume text against predefined parameters and returns a score
out of 100 plus a breakdown.

STATUS: Baseline heuristic version is implemented so the app runs
end-to-end. This is intentionally simple (rule-based, per project scope
limits — no ML/deep learning).

>>> ANTIGRAVITY MISSION TARGET <<<
Ask your agent to improve `score_resume()`:
- Better section detection (regex is naive right now — e.g. "Skills"
  header detection will miss "Technical Skills", "Core Competencies", etc.)
- Weight the 6 parameters from the project brief more carefully:
  resume structure, skills section, education details, projects section,
  contact information, resume completeness (currently equal-weighted).
- Return more useful sub-scores for the dashboard.
Do NOT introduce ML model training — keep this rule-based per project scope.
"""
import re

SECTION_PATTERNS = {
    "education": r"\b(education|academic background|qualification)\b",
    "skills": r"\b(skills|technical skills|core competencies)\b",
    "projects": r"\b(projects|personal projects|academic projects)\b",
    "experience": r"\b(experience|internship|work history)\b",
}

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"


def score_resume(text: str) -> dict:
    """
    Returns a dict like:
    {
        "total_score": 78,
        "breakdown": {
            "structure": 15,       # out of 20
            "skills_section": 15,  # out of 15
            "education": 15,       # out of 15
            "projects": 20,        # out of 20
            "contact_info": 10,    # out of 15
            "completeness": 3      # out of 15 (based on word count)
        }
    }
    """
    text_lower = text.lower()
    breakdown = {}

    # Structure: does it have clear section headers at all?
    sections_found = sum(1 for pat in SECTION_PATTERNS.values() if re.search(pat, text_lower))
    breakdown["structure"] = round((sections_found / len(SECTION_PATTERNS)) * 20)

    breakdown["skills_section"] = 15 if re.search(SECTION_PATTERNS["skills"], text_lower) else 0
    breakdown["education"] = 15 if re.search(SECTION_PATTERNS["education"], text_lower) else 0
    breakdown["projects"] = 20 if re.search(SECTION_PATTERNS["projects"], text_lower) else 0

    has_email = bool(re.search(EMAIL_REGEX, text))
    has_phone = bool(re.search(PHONE_REGEX, text))
    breakdown["contact_info"] = (10 if has_email else 0) + (5 if has_phone else 0)

    # Completeness: rough proxy using word count (too short = incomplete resume)
    word_count = len(text.split())
    if word_count >= 300:
        breakdown["completeness"] = 15
    elif word_count >= 150:
        breakdown["completeness"] = 8
    else:
        breakdown["completeness"] = 2

    total_score = sum(breakdown.values())
    return {"total_score": min(total_score, 100), "breakdown": breakdown}
