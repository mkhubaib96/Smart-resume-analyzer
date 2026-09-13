# Smart Resume Analyzer with AI-Based Feedback

AI capstone project — Flask + rule-based NLP resume analysis.

## Stack
- Backend: Python Flask
- Frontend: Jinja2 templates + Bootstrap 5
- Storage: SQLite (via `resume_analyzer/db.py`)
- Deployment: Render

## Local setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

## Module status

| Module | Status | File(s) |
|---|---|---|
| 1. Resume Upload & Parsing | ✅ Done | `resume_analyzer/parser.py`, `resume_analyzer/db.py` |
| 2. Resume Score Analyzer | 🟡 Baseline works, needs refinement | `resume_analyzer/scorer.py` |
| 3. ATS Keyword Checker | 🟡 Baseline works, needs refinement | `resume_analyzer/ats_checker.py`, `data/role_keywords.json` |
| 4. Smart Feedback System | 🟡 Baseline works, needs refinement | `resume_analyzer/feedback.py` |
| 5. Dashboard & Report Generation | 🟡 Plain but functional | `templates/dashboard.html` |

Every module file with a 🟡 status has an `>>> ANTIGRAVITY MISSION TARGET <<<`
docstring block at the top describing exactly what to improve. Use those as
your mission prompts (see below) so the agent has minimal ambiguity to
resolve — this saves credits vs. one giant "build everything" prompt.

## Deploying to Render (free tier)

1. Push this repo to GitHub.
2. On [render.com](https://render.com), New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add an environment variable `SECRET_KEY` with any random string.
6. Deploy. Note: Render's free tier spins down after inactivity — first
   request after idle will be slow (~30s), that's normal.

## Antigravity mission prompts (paste one at a time, in Plan Mode)

**Mission A — Improve resume scoring (Module 2):**
> Open `resume_analyzer/scorer.py` and read the ANTIGRAVITY MISSION TARGET
> docstring at the top. Improve `score_resume()` per the TODOs there:
> better section header detection (handle synonyms like "Technical Skills",
> "Core Competencies"), and re-balance the 6 score components. Keep it
> rule-based (regex/string logic only, no ML). Update or add tests if a
> `tests/` folder exists. Don't change the function signature or return
> shape — `app.py` depends on it.

**Mission B — Improve ATS keyword matching (Module 3):**
> Open `resume_analyzer/ats_checker.py` and `data/role_keywords.json`.
> Improve `check_ats()` per the TODOs in the docstring: add a synonym map
> (e.g. JS ↔ JavaScript, ML ↔ Machine Learning) and use
> `difflib.get_close_matches` for near-miss fuzzy matching. Keep the return
> shape (`ats_score`, `matched_keywords`, `missing_keywords`) unchanged.

**Mission C — Improve feedback suggestions (Module 4):**
> Open `resume_analyzer/feedback.py`. Improve `generate_feedback()` per the
> TODOs: add more varied, specific suggestion templates, and prioritize by
> impact (most important issue first). Keep the function signature
> unchanged since `app.py` calls it directly.

**Mission D — Polish the dashboard (Module 5):**
> Open `templates/dashboard.html`. Add a Chart.js bar chart visualizing
> `analysis.score_breakdown`, and add a print/download-as-PDF button using
> the browser's print dialog (`window.print()` with a print stylesheet is
> fine — no server-side PDF generation needed). Keep all existing Jinja
> variables intact.

**Mission E — Tests + deployment check:**
> Add a `tests/` folder with pytest tests for `scorer.py`, `ats_checker.py`,
> and `feedback.py` using sample resume text fixtures. Then verify the app
> runs cleanly with `gunicorn app:app` locally (matching the Render start
> command) before I deploy.

Do these one at a time in separate missions — each is scoped to 1-2 files,
which keeps Plan Mode fast and avoids the agent re-exploring the whole repo
every time.
