"""
Unit tests for resume_analyzer/scorer.py
Run with: python -m pytest tests/ -v
"""
import sys
import os
import unittest

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resume_analyzer.scorer import score_resume

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_TEXT = "John Doe"

SKILLS_SYNONYM_TEXTS = [
    # Various synonym headers for skills
    "Core Competencies\nPython, SQL, Java, Docker, AWS, Git\n" * 5,
    "Technical Skills\nReact, Node.js, MongoDB, REST APIs, TypeScript\n" * 5,
    "Tech Stack\nFlask, PostgreSQL, Redis, Celery, Nginx\n" * 5,
    "Areas of Expertise\nMachine Learning, Data Analysis, TensorFlow\n" * 5,
    "Proficiencies\nC++, OpenCV, Linux, Bash, Kubernetes\n" * 5,
]

EDU_SYNONYM_TEXTS = [
    "Academic Qualifications\nBachelor of Technology, XYZ University, 2022",
    "Academics\nM.S. Computer Science, ABC University, 2023",
    "Coursework\nB.Sc. Information Technology, DEF College, 2021",
    # Degree keyword without a header (partial credit)
    "Graduated with a B.Tech from State University in 2020.",
]

FULL_RESUME = """
John Doe
john.doe@example.com | +1-555-123-4567

Education
B.Tech in Computer Science, MIT, 2022

Technical Skills
Python, SQL, Machine Learning, Docker, Kubernetes, Git, REST APIs, CI/CD

Professional Experience
Software Engineer, Acme Corp, Jan 2022 – Present
  - Built scalable microservices using Flask and PostgreSQL.
  - Reduced deployment time by 40% via Docker automation.

Projects
Smart Resume Analyzer
  - A web app to score and analyze resumes using NLP techniques.
  - Python, Flask, SQLite, Bootstrap

Portfolio Manager
  - Investment tracking dashboard with live market data.
  - React, Node.js, MongoDB

Contact Details
john.doe@example.com | +1-555-123-4567 | linkedin.com/in/johndoe
""" * 2   # repeat to easily exceed 300 words


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestScoreResumeReturnShape(unittest.TestCase):
    """Return value must always match the expected contract."""

    REQUIRED_BREAKDOWN_KEYS = {
        "structure", "skills_section", "education",
        "projects", "contact_info", "completeness",
    }

    def _assert_shape(self, result):
        self.assertIn("total_score", result)
        self.assertIn("breakdown", result)
        self.assertIsInstance(result["total_score"], int)
        self.assertGreaterEqual(result["total_score"], 0)
        self.assertLessEqual(result["total_score"], 100)
        self.assertEqual(set(result["breakdown"].keys()), self.REQUIRED_BREAKDOWN_KEYS)

    def test_return_shape_minimal(self):
        self._assert_shape(score_resume(MINIMAL_TEXT))

    def test_return_shape_full(self):
        self._assert_shape(score_resume(FULL_RESUME))

    def test_total_score_does_not_exceed_100(self):
        result = score_resume(FULL_RESUME)
        self.assertLessEqual(result["total_score"], 100)


class TestEmptyResume(unittest.TestCase):
    def test_empty_string_gives_low_score(self):
        result = score_resume("")
        self.assertLess(result["total_score"], 20)

    def test_minimal_text_no_crash(self):
        result = score_resume(MINIMAL_TEXT)
        self.assertIsInstance(result["total_score"], int)


class TestSynonymSkillsDetection(unittest.TestCase):
    """Synonym headers must trigger skills_section score > 0."""

    def test_core_competencies_header(self):
        result = score_resume(SKILLS_SYNONYM_TEXTS[0])
        self.assertGreater(result["breakdown"]["skills_section"], 0,
                           "Core Competencies header not detected")

    def test_technical_skills_header(self):
        result = score_resume(SKILLS_SYNONYM_TEXTS[1])
        self.assertGreater(result["breakdown"]["skills_section"], 0,
                           "Technical Skills header not detected")

    def test_tech_stack_header(self):
        result = score_resume(SKILLS_SYNONYM_TEXTS[2])
        self.assertGreater(result["breakdown"]["skills_section"], 0,
                           "Tech Stack header not detected")

    def test_areas_of_expertise_header(self):
        result = score_resume(SKILLS_SYNONYM_TEXTS[3])
        self.assertGreater(result["breakdown"]["skills_section"], 0,
                           "Areas of Expertise header not detected")


class TestSynonymEducationDetection(unittest.TestCase):
    """Synonym headers + degree keywords must trigger education score."""

    def test_academic_qualifications_header(self):
        result = score_resume(EDU_SYNONYM_TEXTS[0])
        self.assertGreater(result["breakdown"]["education"], 0,
                           "Academic Qualifications header not detected")

    def test_academics_ms_header(self):
        result = score_resume(EDU_SYNONYM_TEXTS[1])
        self.assertGreater(result["breakdown"]["education"], 0,
                           "Academics / M.S. not detected")

    def test_degree_keyword_without_header_gives_partial(self):
        """Degree keyword alone (no header) should earn partial credit (8)."""
        result = score_resume(EDU_SYNONYM_TEXTS[3])
        self.assertEqual(result["breakdown"]["education"], 8,
                         "Degree keyword without header should give 8 pts (partial credit)")


class TestContactInfo(unittest.TestCase):
    def test_full_contact_gives_15(self):
        text = "jane@example.com +1-555-999-8888"
        result = score_resume(text)
        self.assertEqual(result["breakdown"]["contact_info"], 15)

    def test_email_only_gives_8(self):
        text = "jane@example.com"
        result = score_resume(text)
        self.assertEqual(result["breakdown"]["contact_info"], 8)

    def test_no_contact_gives_0(self):
        text = "No contact information here at all."
        result = score_resume(text)
        self.assertEqual(result["breakdown"]["contact_info"], 0)


class TestCompletenessThresholds(unittest.TestCase):
    def test_over_300_words_gives_15(self):
        text = "word " * 350
        result = score_resume(text)
        self.assertEqual(result["breakdown"]["completeness"], 15)

    def test_150_to_299_words_gives_8(self):
        text = "word " * 200
        result = score_resume(text)
        self.assertEqual(result["breakdown"]["completeness"], 8)

    def test_under_150_words_gives_2(self):
        text = "word " * 50
        result = score_resume(text)
        self.assertEqual(result["breakdown"]["completeness"], 2)


class TestFullResume(unittest.TestCase):
    def test_full_resume_scores_highly(self):
        result = score_resume(FULL_RESUME)
        self.assertGreaterEqual(result["total_score"], 60,
                                "A complete resume with all sections should score ≥60")

    def test_full_resume_all_breakdown_nonzero(self):
        result = score_resume(FULL_RESUME)
        for key, val in result["breakdown"].items():
            self.assertGreater(val, 0, f"Expected {key} > 0 for full resume, got {val}")


if __name__ == "__main__":
    unittest.main()
