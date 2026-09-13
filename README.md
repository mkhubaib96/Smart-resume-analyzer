# Smart Resume Analyzer with AI-Based Feedback

An AI-powered web application that analyzes resumes against industry hiring
standards — checking ATS compatibility, resume structure, and role-specific
skill gaps — and generates personalized improvement suggestions.

Built as an AI Capstone Project simulating features used in real-world
HR-Tech and recruitment platforms.

**Live Demo:** https://smart-resume-analyzer-3tum.onrender.com

> Note: hosted on Render's free tier — the app sleeps after ~15 min of
> inactivity, so the first request after idle can take 20–30 seconds to
> wake up.

---

## Features

- **Resume Upload & Parsing** — upload resumes in PDF or DOCX format, text extracted automatically
- **Resume Score Analyzer** — scores resumes out of 100 across 6 parameters (structure, skills, education, projects, contact info, completeness)
- **ATS Keyword Checker** — compares resume content against role-specific keyword sets (Data Analyst, Web Developer, AI Engineer, Cloud Engineer) with synonym and fuzzy matching
- **Smart Feedback System** — generates prioritized, specific improvement suggestions based on the analysis
- **Interactive Dashboard** — visualizes score breakdown, ATS match %, missing skills, and suggestions, with a downloadable report view
- **Analysis History** — every analysis is stored and browsable via a history page

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python (Flask) |
| Frontend | Jinja2 templates, Bootstrap 5, Chart.js |
| Storage | SQLite |
| Deployment | Render |

All analysis logic is **rule-based** (regex, keyword matching, heuristics) —
no ML model training or third-party LLM calls, per project scope.

## Project Structure

```
smart-resume-analyzer/
├── app.py                      # Flask routes
├── resume_analyzer/
│   ├── parser.py                # Module 1: PDF/DOCX text extraction
│   ├── db.py                    # SQLite storage
│   ├── scorer.py                # Module 2: Resume scoring
│   ├── ats_checker.py           # Module 3: ATS keyword matching
│   └── feedback.py              # Module 4: Suggestion generation
├── templates/                   # Module 5: Dashboard & UI
├── data/role_keywords.json      # Role-specific keyword sets
├── tests/                       # Unit tests (pytest)
└── requirements.txt
```

## Running Locally

```bash
git clone https://github.com/mkhubaib96/Smart-resume-analyzer.git
cd Smart-resume-analyzer
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`

## Running Tests

```bash
python -m pytest tests/ -v
```

## Deployment (Render)

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment variable:** `SECRET_KEY` (any random string)

## Learning Outcomes

This project covers practical exposure to:
- File handling and text extraction from documents
- Rule-based NLP / keyword extraction and matching
- Web application development with Flask
- Dashboard creation and data visualization
- End-to-end deployment workflows

## Scope Limitations

Per project brief, intentionally excludes: deep learning models, LLM
training, complex recommendation engines, enterprise-level authentication,
and large-scale cloud architecture — focus is a clean, functional,
industry-oriented prototype.
