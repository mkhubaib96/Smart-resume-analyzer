"""
Module 3: ATS Keyword Checker
--------------------------------
Compares resume text against role-specific keyword lists
(data/role_keywords.json) and returns an ATS compatibility score plus
missing keywords.

STATUS: Baseline implementation works (simple case-insensitive substring
match). This is intentionally simple — matches "Basic NLP concepts" /
"Keyword extraction" learning outcome from the brief without needing
spaCy/NLTK.

>>> ANTIGRAVITY MISSION TARGET <<<
Ask your agent to improve `check_ats()`:
- Handle keyword variants/synonyms (e.g. "JS" should match "JavaScript",
  "ML" should match "Machine Learning") — a small synonym map in
  role_keywords.json or a new synonyms.json is enough, no ML needed.
- Handle plural/singular and common abbreviations.
- Consider fuzzy matching for near-misses (e.g. difflib.get_close_matches)
  — still rule-based, no LLM calls, per project scope.
"""
import json
import os

KEYWORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "role_keywords.json")


def load_role_keywords() -> dict:
    with open(KEYWORDS_PATH, "r") as f:
        return json.load(f)


def get_available_roles() -> list:
    return list(load_role_keywords().keys())


def check_ats(text: str, target_role: str) -> dict:
    """
    Returns:
    {
        "ats_score": 70,               # % of role keywords found
        "matched_keywords": [...],
        "missing_keywords": [...]
    }
    """
    role_keywords = load_role_keywords()
    keywords = role_keywords.get(target_role, [])
    if not keywords:
        return {"ats_score": 0, "matched_keywords": [], "missing_keywords": []}

    text_lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    missing = [kw for kw in keywords if kw not in matched]

    ats_score = round((len(matched) / len(keywords)) * 100)
    return {"ats_score": ats_score, "matched_keywords": matched, "missing_keywords": missing}
