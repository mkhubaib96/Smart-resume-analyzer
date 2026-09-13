"""
Module 4: Smart Feedback System
----------------------------------
Turns the scorer + ATS checker output into human-readable improvement
suggestions.

STATUS: Improved — suggestions are now prioritized by recruiter/ATS impact
(most critical issue first) and each weak area has multiple specific,
varied templates rather than a single generic message.

Improvements over baseline:
- Priority-ordered output: contact info → skills → structure → projects →
  education → completeness → missing keywords
- Graded templates: different messages depending on HOW weak the score is
  (e.g. 0 vs low-but-present vs moderate)
- More specific, actionable language per section
- Missing keywords surfaced with role-specific framing, capped at 5
Keep it rule-based / template-driven — no LLM calls, per project scope.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Suggestion builders — one function per section, returning (priority, text)
# Priority 1 = most impactful (shown first). Higher number = lower priority.
# ---------------------------------------------------------------------------

def _contact_suggestions(score: int) -> list[tuple[int, str]]:
    """Max 15 — email=8, phone=7."""
    results = []
    if score == 0:
        results.append((1, (
            "⚠️ No contact information detected. Add your email address and "
            "phone number at the top — recruiters cannot reach you without it."
        )))
    elif score <= 8:
        results.append((1, (
            "Your resume is missing a phone number. Add it alongside your email "
            "so recruiters have a second way to contact you."
        )))
    return results


def _skills_suggestions(score: int) -> list[tuple[int, str]]:
    """Max 20."""
    results = []
    if score == 0:
        results.append((2, (
            "Add a dedicated 'Skills' (or 'Technical Skills') section listing your "
            "key tools, languages, and technologies — ATS scanners look for this first."
        )))
    elif score <= 10:
        results.append((2, (
            "Your skills section exists but appears sparse. Expand it with 8–12 "
            "specific technologies, tools, or frameworks relevant to your target role."
        )))
    return results


def _structure_suggestions(score: int) -> list[tuple[int, str]]:
    """Max 20 — 5 pts per section found."""
    results = []
    if score == 0:
        results.append((3, (
            "Your resume lacks clear section headers. Add labelled sections such as "
            "'Education', 'Skills', 'Projects', and 'Experience' so ATS systems can "
            "parse your content correctly."
        )))
    elif score <= 10:
        results.append((3, (
            "Only 1–2 standard sections were detected. Ensure your resume has at "
            "least four clearly labeled sections (Education, Skills, Projects, "
            "Experience) to pass most ATS filters."
        )))
    elif score < 20:
        results.append((3, (
            "Most sections were found, but consider adding a dedicated 'Experience' "
            "or 'Work History' section if you have relevant internships or jobs."
        )))
    return results


def _projects_suggestions(score: int) -> list[tuple[int, str]]:
    """Max 15."""
    results = []
    if score == 0:
        results.append((4, (
            "Add a 'Projects' section with at least 2 technical projects. For each, "
            "describe the problem, your solution, the tech stack used, and any "
            "measurable impact (e.g. 'reduced load time by 30%%')."
        )))
    elif score <= 8:
        results.append((4, (
            "A projects section was detected but only one project entry was found. "
            "Add a second distinct project to make your portfolio more convincing."
        )))
    return results


def _education_suggestions(score: int) -> list[tuple[int, str]]:
    """Max 15."""
    results = []
    if score == 0:
        results.append((5, (
            "No education section or degree keyword was found. Add an 'Education' "
            "section with your degree, institution, and graduation year."
        )))
    elif score <= 8:
        results.append((5, (
            "Your degree was mentioned but without a dedicated 'Education' section. "
            "Move it under a clear header with your institution name and GPA (if above 3.0)."
        )))
    return results


def _completeness_suggestions(score: int) -> list[tuple[int, str]]:
    """Max 15 — based on word count proxy."""
    results = []
    if score <= 2:
        results.append((6, (
            "Your resume appears very short (under ~150 words). "
            "Expand each section with bullet points describing responsibilities, "
            "tools used, and outcomes — aim for 300–600 words total."
        )))
    elif score <= 8:
        results.append((6, (
            "Your resume is somewhat brief. Consider adding more detail under "
            "each project or experience entry, including your specific contributions "
            "and measurable results."
        )))
    return results


def _keyword_suggestions(missing_keywords: list[str]) -> list[tuple[int, str]]:
    """Surface top missing ATS keywords as role-specific suggestions."""
    results = []
    for kw in missing_keywords[:5]:  # cap to avoid overwhelming the user
        results.append((7, (
            f"Consider adding '{kw}' to your resume if you have relevant "
            f"experience — it's a commonly expected skill for this role."
        )))
    return results


# ---------------------------------------------------------------------------
# Public API — signature UNCHANGED
# ---------------------------------------------------------------------------

def generate_feedback(score_breakdown: dict, missing_keywords: list) -> list:
    """
    Returns a list of suggestion strings, ordered from most to least impactful.

    Priority (descending impact):
      1. Contact info (recruiter literally cannot reach you if missing)
      2. Skills section (ATS scans this most heavily)
      3. Resume structure (ATS parsing depends on clear headers)
      4. Projects (demonstrates real-world capability)
      5. Education (basic credential signal)
      6. Completeness (length/depth proxy)
      7. Missing role keywords (targeted ATS improvement)
    """
    raw: list[tuple[int, str]] = []

    raw += _contact_suggestions(score_breakdown.get("contact_info", 0))
    raw += _skills_suggestions(score_breakdown.get("skills_section", 0))
    raw += _structure_suggestions(score_breakdown.get("structure", 0))
    raw += _projects_suggestions(score_breakdown.get("projects", 0))
    raw += _education_suggestions(score_breakdown.get("education", 0))
    raw += _completeness_suggestions(score_breakdown.get("completeness", 0))
    raw += _keyword_suggestions(missing_keywords)

    # Sort by priority (stable sort preserves insertion order within same level)
    raw.sort(key=lambda x: x[0])
    suggestions = [text for _, text in raw]

    if not suggestions:
        suggestions.append(
            "Your resume covers all key sections well and includes strong contact "
            "details. To go further, tailor your keywords and project descriptions "
            "to each specific job description."
        )

    return suggestions
