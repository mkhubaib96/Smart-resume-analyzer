"""
Module 4: Smart Feedback System
----------------------------------
Turns the scorer + ATS checker output into human-readable improvement
suggestions.

STATUS: Baseline implementation works (template-based rules).

>>> ANTIGRAVITY MISSION TARGET <<<
Ask your agent to improve `generate_feedback()`:
- More specific, varied suggestion templates per weak area.
- Prioritize suggestions (most impactful first) instead of a flat list.
- Pull in missing_keywords from ats_checker to suggest specific skills
  to add (e.g. "Add SQL skill" per the project brief's example).
Keep it rule-based / template-driven — no LLM calls, per project scope.
"""


def generate_feedback(score_breakdown: dict, missing_keywords: list) -> list:
    """Returns a list of suggestion strings."""
    suggestions = []

    if score_breakdown.get("structure", 0) < 15:
        suggestions.append("Improve resume formatting with clear section headers (Education, Skills, Projects, Experience).")

    if score_breakdown.get("skills_section", 0) == 0:
        suggestions.append("Add a dedicated Skills section listing your technical skills.")

    if score_breakdown.get("projects", 0) == 0:
        suggestions.append("Add a Projects section — include at least 1-2 technical projects with impact/results.")

    if score_breakdown.get("contact_info", 0) < 15:
        suggestions.append("Include both an email address and phone number in your contact details.")

    if score_breakdown.get("completeness", 0) < 8:
        suggestions.append("Your resume looks short — consider expanding on your experience, projects, or certifications.")

    for kw in missing_keywords[:5]:  # cap suggestions to avoid overwhelming the user
        suggestions.append(f"Consider adding '{kw}' if you have relevant experience — it's expected for this role.")

    if not suggestions:
        suggestions.append("Your resume covers the key sections well. Consider tailoring keywords per job description.")

    return suggestions
