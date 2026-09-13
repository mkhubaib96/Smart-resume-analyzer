"""
Module 3: ATS Keyword Checker
--------------------------------
Compares resume text against role-specific keyword lists
(data/role_keywords.json) and returns an ATS compatibility score plus
missing keywords.

STATUS: Improved — synonym expansion (data/synonyms.json) and
difflib near-miss fuzzy matching added. Still entirely rule-based;
no ML/LLM calls used, per project scope.

Improvements over baseline:
- Synonym map (data/synonyms.json): abbreviations & common variants
  are expanded before matching (JS→JavaScript, ML→Machine Learning…)
- Fuzzy matching via difflib.get_close_matches for near-misses
  (e.g. "Tensorflow" ≈ "TensorFlow", "scikit_learn" ≈ "Scikit-learn")
- Plural/singular handled by simple suffix-strip heuristic
"""
import difflib
import json
import os
import re

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
KEYWORDS_PATH = os.path.join(_DATA_DIR, "role_keywords.json")
SYNONYMS_PATH = os.path.join(_DATA_DIR, "synonyms.json")

# Fuzzy-match tuning
_FUZZY_CUTOFF = 0.82   # similarity threshold (0–1); lower = more permissive
_FUZZY_MAX = 1         # only the single best near-miss per keyword


# ---------------------------------------------------------------------------
# Data loaders (cached at module level after first call)
# ---------------------------------------------------------------------------

_ROLE_KEYWORDS_CACHE: dict | None = None
_SYNONYMS_CACHE: dict | None = None


def _load_role_keywords() -> dict:
    global _ROLE_KEYWORDS_CACHE
    if _ROLE_KEYWORDS_CACHE is None:
        with open(KEYWORDS_PATH, "r") as f:
            _ROLE_KEYWORDS_CACHE = json.load(f)
    return _ROLE_KEYWORDS_CACHE


def _load_synonyms() -> dict:
    """Returns {canonical_keyword: [synonym, ...]} (all lower-cased values)."""
    global _SYNONYMS_CACHE
    if _SYNONYMS_CACHE is None:
        if os.path.exists(SYNONYMS_PATH):
            with open(SYNONYMS_PATH, "r") as f:
                raw = json.load(f)
            # Drop the _comment key if present; lower-case all synonym strings
            _SYNONYMS_CACHE = {
                k: [s.lower() for s in v]
                for k, v in raw.items()
                if not k.startswith("_")
            }
        else:
            _SYNONYMS_CACHE = {}
    return _SYNONYMS_CACHE


# ---------------------------------------------------------------------------
# Public API (unchanged names)
# ---------------------------------------------------------------------------

def load_role_keywords() -> dict:
    return _load_role_keywords()


def get_available_roles() -> list:
    return list(_load_role_keywords().keys())


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _simple_stem(word: str) -> str:
    """
    Very lightweight suffix-stripping so plural/gerund variants match.
    e.g. 'visualizations' → 'visualization', 'testing' → 'test'
    """
    for suffix in ("ations", "ation", "ings", "ing", "ies", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: len(word) - len(suffix)]
    return word


def _build_resume_tokens(text: str) -> set:
    """
    Tokenize the resume into a set of normalised strings used for
    fuzzy / stem matching.  We keep:
      - the full lower-cased text (for substring checks)
      - individual lower-cased words
      - stemmed forms of individual words
    """
    text_lower = text.lower()
    # Split on whitespace and common separators
    words = re.split(r"[\s,;|•·/\-]+", text_lower)
    tokens = set(words)
    tokens.update(_simple_stem(w) for w in words if w)
    return tokens


def _keyword_in_text(keyword: str, text_lower: str,
                     resume_tokens: set, synonyms: dict) -> bool:
    """
    Return True if *keyword* (or any of its synonyms) is found in the
    resume, using three layers of matching:

    1. Direct substring match (original baseline behaviour).
    2. Synonym expansion — any entry in synonyms[keyword] is also
       tried as a substring.
    3. Fuzzy token match — difflib compares keyword (and synonyms)
       against individual resume tokens for near-misses.
    """
    kw_lower = keyword.lower()

    # Layer 1 — direct substring
    if kw_lower in text_lower:
        return True

    # Gather all forms to test (canonical + synonyms)
    forms = [kw_lower] + synonyms.get(keyword, [])

    # Layer 2 — synonym substring search
    for form in forms[1:]:          # canonical already checked above
        if form in text_lower:
            return True

    # Layer 3 — fuzzy token match
    # Build the candidate word-list once (done by caller via resume_tokens)
    candidate_list = list(resume_tokens)
    for form in forms:
        matches = difflib.get_close_matches(
            form, candidate_list,
            n=_FUZZY_MAX, cutoff=_FUZZY_CUTOFF
        )
        if matches:
            return True

    return False


# ---------------------------------------------------------------------------
# Core public function — signature & return shape UNCHANGED
# ---------------------------------------------------------------------------

def check_ats(text: str, target_role: str) -> dict:
    """
    Returns:
    {
        "ats_score": 70,               # % of role keywords found
        "matched_keywords": [...],
        "missing_keywords": [...]
    }

    Matching strategy (in order):
    1. Case-insensitive substring  (original baseline)
    2. Synonym / abbreviation map  (data/synonyms.json)
    3. difflib near-miss fuzzy     (cutoff=0.82 on individual tokens)
    """
    role_keywords = _load_role_keywords()
    keywords = role_keywords.get(target_role, [])
    if not keywords:
        return {"ats_score": 0, "matched_keywords": [], "missing_keywords": []}

    synonyms = _load_synonyms()
    text_lower = text.lower()
    resume_tokens = _build_resume_tokens(text)

    matched = []
    missing = []
    for kw in keywords:
        if _keyword_in_text(kw, text_lower, resume_tokens, synonyms):
            matched.append(kw)
        else:
            missing.append(kw)

    ats_score = round((len(matched) / len(keywords)) * 100)
    return {
        "ats_score": ats_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }
