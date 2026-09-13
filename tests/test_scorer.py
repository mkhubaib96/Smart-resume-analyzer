"""
Unit tests for resume_analyzer/scorer.py and resume_analyzer/ats_checker.py
Run with: python -m pytest tests/ -v
"""
import sys
import os
import unittest

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resume_analyzer.scorer import score_resume
from resume_analyzer.ats_checker import check_ats, _load_synonyms

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


# ===========================================================================
# ATS Checker Tests
# ===========================================================================

class TestCheckAtsReturnShape(unittest.TestCase):
    """Return value contract must always hold."""

    REQUIRED_KEYS = {"ats_score", "matched_keywords", "missing_keywords"}

    def test_known_role_has_all_keys(self):
        result = check_ats("Python SQL Pandas NumPy Excel", "Data Analyst")
        self.assertEqual(set(result.keys()), self.REQUIRED_KEYS)

    def test_unknown_role_returns_zeros(self):
        result = check_ats("Python SQL", "Nonexistent Role")
        self.assertEqual(result["ats_score"], 0)
        self.assertEqual(result["matched_keywords"], [])
        self.assertEqual(result["missing_keywords"], [])

    def test_score_is_integer_between_0_and_100(self):
        result = check_ats("Python Machine Learning", "AI Engineer")
        self.assertIsInstance(result["ats_score"], int)
        self.assertGreaterEqual(result["ats_score"], 0)
        self.assertLessEqual(result["ats_score"], 100)

    def test_matched_plus_missing_equals_all_keywords(self):
        result = check_ats("Python SQL Tableau", "Data Analyst")
        total = len(result["matched_keywords"]) + len(result["missing_keywords"])
        from resume_analyzer.ats_checker import _load_role_keywords
        expected = len(_load_role_keywords()["Data Analyst"])
        self.assertEqual(total, expected)


class TestAtsDirectMatch(unittest.TestCase):
    """Original baseline — direct substring — must still work."""

    def test_exact_keyword_matched(self):
        result = check_ats("I have experience with Python and SQL.", "Data Analyst")
        self.assertIn("Python", result["matched_keywords"])
        self.assertIn("SQL", result["matched_keywords"])

    def test_case_insensitive_match(self):
        result = check_ats("proficient in PYTHON and sql", "Data Analyst")
        self.assertIn("Python", result["matched_keywords"])
        self.assertIn("SQL", result["matched_keywords"])


class TestAtsSynonymMatching(unittest.TestCase):
    """Synonym map must let abbreviations count as matches."""

    def test_js_matches_javascript(self):
        """Resume says 'JS'; keyword is 'JavaScript'."""
        result = check_ats(
            "Skills: JS, React, Node.js, CSS, HTML, Git, REST API, MongoDB, Responsive Design, TypeScript",
            "Web Developer"
        )
        self.assertIn("JavaScript", result["matched_keywords"],
                      "'JS' in resume should match canonical keyword 'JavaScript'")

    def test_ml_matches_machine_learning(self):
        """Resume says 'ML'; keyword is 'Machine Learning'."""
        result = check_ats(
            "Python ML TensorFlow PyTorch NLP Scikit-learn Deep Learning Data Preprocessing Model Deployment Pandas",
            "AI Engineer"
        )
        self.assertIn("Machine Learning", result["matched_keywords"],
                      "'ML' in resume should match 'Machine Learning'")

    def test_k8s_matches_kubernetes(self):
        """Resume says 'K8s'; keyword is 'Kubernetes'."""
        result = check_ats(
            "AWS Azure GCP Docker K8s CI/CD Terraform Linux Cloud Security Networking",
            "Cloud Engineer"
        )
        self.assertIn("Kubernetes", result["matched_keywords"],
                      "'K8s' should match 'Kubernetes'")

    def test_nodejs_alias_matches(self):
        """Resume uses 'NodeJS'; keyword is 'Node.js'."""
        result = check_ats(
            "HTML CSS JavaScript React NodeJS REST API Git Responsive Design TypeScript MongoDB",
            "Web Developer"
        )
        self.assertIn("Node.js", result["matched_keywords"],
                      "'NodeJS' should match 'Node.js'")

    def test_sklearn_matches_scikit_learn(self):
        """Resume says 'sklearn'; keyword is 'Scikit-learn'."""
        result = check_ats(
            "Python Machine Learning TensorFlow PyTorch NLP sklearn Deep Learning Data Preprocessing Model Deployment Pandas",
            "AI Engineer"
        )
        self.assertIn("Scikit-learn", result["matched_keywords"],
                      "'sklearn' should match 'Scikit-learn'")

    def test_powerbi_alias(self):
        """Resume uses 'PowerBI'; keyword is 'Power BI'."""
        result = check_ats(
            "SQL Excel Python PowerBI Tableau Statistics Data Visualization Pandas NumPy A/B Testing",
            "Data Analyst"
        )
        self.assertIn("Power BI", result["matched_keywords"],
                      "'PowerBI' should match 'Power BI'")


class TestAtsFuzzyMatching(unittest.TestCase):
    """difflib fuzzy matching should catch close misspellings / casing variants."""

    def test_tensorflow_casing_variant(self):
        """'Tensorflow' (wrong case) should fuzzy-match 'TensorFlow'."""
        result = check_ats(
            "Python Machine Learning Tensorflow PyTorch NLP Scikit-learn Deep Learning Data Preprocessing Model Deployment Pandas",
            "AI Engineer"
        )
        self.assertIn("TensorFlow", result["matched_keywords"],
                      "'Tensorflow' should fuzzy-match 'TensorFlow'")

    def test_synonyms_json_loaded(self):
        """synonyms.json must be loadable and non-empty."""
        syns = _load_synonyms()
        self.assertGreater(len(syns), 0, "synonyms.json should have entries")
        self.assertIn("JavaScript", syns, "'JavaScript' must be a canonical entry")
        self.assertIn("js", syns["JavaScript"], "'js' must be a synonym of 'JavaScript'")


class TestAtsPluralStemming(unittest.TestCase):
    """Plural/gerund variants in the resume should still count as matches."""

    def test_visualization_plural_matches_data_visualization(self):
        """Resume has 'visualizations'; keyword is 'Data Visualization'."""
        result = check_ats(
            "SQL Excel Python Power BI Tableau Statistics visualizations Pandas NumPy A/B Testing",
            "Data Analyst"
        )
        self.assertIn("Data Visualization", result["matched_keywords"],
                      "Plural 'visualizations' should match 'Data Visualization'")


class TestAtsFullRoleCoverage(unittest.TestCase):
    """A resume that explicitly lists all role keywords should score 100."""

    def test_full_match_web_developer(self):
        text = "HTML CSS JavaScript React Node.js REST API Git Responsive Design TypeScript MongoDB"
        result = check_ats(text, "Web Developer")
        self.assertEqual(result["ats_score"], 100,
                         "All keywords present verbatim — expect 100% ATS score")
        self.assertEqual(result["missing_keywords"], [])

    def test_full_match_cloud_engineer(self):
        text = "AWS Azure GCP Docker Kubernetes CI/CD Terraform Linux Cloud Security Networking"
        result = check_ats(text, "Cloud Engineer")
        self.assertEqual(result["ats_score"], 100)


if __name__ == "__main__":
    unittest.main()
