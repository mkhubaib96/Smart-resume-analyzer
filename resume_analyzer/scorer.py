"""
Module 2: Resume Score Analyzer
---------------------------------
Analyzes resume text against predefined parameters and returns a score
out of 100 plus a breakdown.

STATUS: Improved heuristic version — better synonym detection and
re-balanced, partial-credit scoring.

>>> ANTIGRAVITY MISSION TARGET <<<
Improvements made:
- Broader section synonym lists (Technical Skills, Core Competencies,
  Professional Experience, Academic Qualifications, Portfolio, etc.)
- Re-balanced weights: skills_section↑20, projects↓15 (total stays 100)
- Partial-credit logic: skills checks actual token count, education
  checks degree keywords, projects checks for multiple project blocks.
Do NOT introduce ML model training — keep this rule-based per project scope.
"""
import re

# ---------------------------------------------------------------------------
# Section detection patterns — each is a broad OR-alternation
# ---------------------------------------------------------------------------
SECTION_PATTERNS = {
    "education": (
        r"\b(education|academic background|academic qualifications?|"
        r"academics?|qualifications?|degrees?|courses?|certifications?|"
        r"educational background)\b"
    ),
    "skills": (
        r"\b(skills|technical skills|core competencies|key skills|"
        r"areas of expertise|technologies|tools\s*(?:&|and)\s*technologies|"
        r"tech stack|proficiencies|technical proficiencies|"
        r"expertise|competencies)\b"
    ),
    "projects": (
        r"\b(projects?|personal projects?|academic projects?|"
        r"portfolio|work samples?|open[\s-]?source|side projects?|"
        r"selected projects?|notable projects?)\b"
    ),
    "experience": (
        r"\b(experience|internship|work history|professional experience|"
        r"employment history|career history|work experience|"
        r"positions? held|relevant experience|industry experience)\b"
    ),
}

# Degree keywords for education partial-credit scoring
_DEGREE_PATTERN = re.compile(
    r"\b(b\.?tech|b\.?e\.?|b\.?s\.?|m\.?s\.?|m\.?tech|mba|ph\.?d|"
    r"bachelor|master|doctorate|associate|diploma|b\.?sc|m\.?sc)\b",
    re.IGNORECASE,
)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,3}[-.s]?)?(\(?\d{3,5}\)?[-.s]?\d{3,4}[-.s]?\d{3,4})"

# Pre-compile section regexes for speed
_COMPILED_SECTIONS = {k: re.compile(v, re.IGNORECASE) for k, v in SECTION_PATTERNS.items()}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _count_skill_tokens(text: str) -> int:
    """
    Rough count of skill-like tokens near a skills header.
    Looks for comma/bullet/pipe separated short phrases (1-4 words each).
    """
    # Find the region after a skills header (up to 600 chars)
    m = _COMPILED_SECTIONS["skills"].search(text)
    if not m:
        return 0
    snippet = text[m.start(): m.start() + 600]
    # Split on common delimiters; count non-empty tokens ≤ 4 words
    raw_tokens = re.split(r"[,•|·\n\r\t]+", snippet)
    count = sum(
        1 for t in raw_tokens
        if t.strip() and 1 <= len(t.strip().split()) <= 4
    )
    return count


def _count_project_blocks(text: str) -> int:
    """
    Estimate how many distinct project entries exist.
    Heuristic: count lines that look like project titles —
    short (≤10 words), Title-Cased or ALL-CAPS, optionally followed by
    a pipe/dash and a year or tech stack hint.
    """
    lines = text.splitlines()
    count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or len(stripped) > 120:
            continue
        words = stripped.split()
        if len(words) < 2 or len(words) > 10:
            continue
        # Must look like a heading: Title Case or ALL CAPS
        if stripped.istitle() or stripped.isupper():
            count += 1
        # Or has a year pattern nearby
        elif re.search(r"\b(20\d{2}|19\d{2})\b", stripped):
            count += 1
    return count


# ---------------------------------------------------------------------------
# Public API — signature and return shape unchanged
# ---------------------------------------------------------------------------

def score_resume(text: str) -> dict:
    """
    Scores a resume from 0–100 and returns a breakdown.

    Returns a dict like:
    {
        "total_score": 78,
        "breakdown": {
            "structure": 15,       # out of 20
            "skills_section": 18,  # out of 20
            "education": 15,       # out of 15
            "projects": 12,        # out of 15
            "contact_info": 15,    # out of 15
            "completeness": 3      # out of 15 (based on word count)
        }
    }
    """
    breakdown: dict = {}

    # ------------------------------------------------------------------
    # 1. STRUCTURE (max 20)
    #    5 pts per section found; count 4 key sections.
    # ------------------------------------------------------------------
    sections_found = sum(
        1 for k, pat in _COMPILED_SECTIONS.items()
        if pat.search(text)
    )
    breakdown["structure"] = min(sections_found * 5, 20)

    # ------------------------------------------------------------------
    # 2. SKILLS SECTION (max 20) — raised from 15
    #    20 if header + ≥5 skill tokens; 10 if header only; 0 otherwise.
    # ------------------------------------------------------------------
    if _COMPILED_SECTIONS["skills"].search(text):
        token_count = _count_skill_tokens(text)
        breakdown["skills_section"] = 20 if token_count >= 5 else 10
    else:
        breakdown["skills_section"] = 0

    # ------------------------------------------------------------------
    # 3. EDUCATION (max 15)
    #    15 if header + degree keyword; 8 if degree keyword only; 0 otherwise.
    # ------------------------------------------------------------------
    has_edu_header = bool(_COMPILED_SECTIONS["education"].search(text))
    has_degree_kw = bool(_DEGREE_PATTERN.search(text))
    if has_edu_header and has_degree_kw:
        breakdown["education"] = 15
    elif has_degree_kw:
        breakdown["education"] = 8
    else:
        breakdown["education"] = 0

    # ------------------------------------------------------------------
    # 4. PROJECTS (max 15) — reduced from 20
    #    15 if header + ≥2 project-like blocks; 8 if header only; 0 otherwise.
    # ------------------------------------------------------------------
    if _COMPILED_SECTIONS["projects"].search(text):
        proj_blocks = _count_project_blocks(text)
        breakdown["projects"] = 15 if proj_blocks >= 2 else 8
    else:
        breakdown["projects"] = 0

    # ------------------------------------------------------------------
    # 5. CONTACT INFO (max 15)
    #    Email = 8 pts, phone = 7 pts.
    # ------------------------------------------------------------------
    has_email = bool(re.search(EMAIL_REGEX, text))
    has_phone = bool(re.search(PHONE_REGEX, text))
    breakdown["contact_info"] = (8 if has_email else 0) + (7 if has_phone else 0)

    # ------------------------------------------------------------------
    # 6. COMPLETENESS (max 15) — word-count proxy; thresholds unchanged.
    # ------------------------------------------------------------------
    word_count = len(text.split())
    if word_count >= 300:
        breakdown["completeness"] = 15
    elif word_count >= 150:
        breakdown["completeness"] = 8
    else:
        breakdown["completeness"] = 2

    total_score = sum(breakdown.values())
    return {"total_score": min(total_score, 100), "breakdown": breakdown}
