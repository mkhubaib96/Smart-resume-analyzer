import os
from flask import Flask, render_template, request, redirect, url_for, flash

from resume_analyzer.parser import extract_text, allowed_file
from resume_analyzer.scorer import score_resume
from resume_analyzer.ats_checker import check_ats, get_available_roles
from resume_analyzer.feedback import generate_feedback
from resume_analyzer import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

db.init_db()


@app.route("/")
def index():
    roles = get_available_roles()
    return render_template("index.html", roles=roles)


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        flash("No file uploaded.")
        return redirect(url_for("index"))

    file = request.files["resume"]
    target_role = request.form.get("target_role")

    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only PDF and DOCX files are supported.")
        return redirect(url_for("index"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        # Module 1
        raw_text = extract_text(filepath)

        # Module 2
        score_result = score_resume(raw_text)

        # Module 3
        ats_result = check_ats(raw_text, target_role)

        # Module 4
        suggestions = generate_feedback(score_result["breakdown"], ats_result["missing_keywords"])

        # Persist (Module 1's "store resume information" + shared storage)
        analysis_id = db.save_analysis(
            filename=file.filename,
            raw_text=raw_text,
            target_role=target_role,
            resume_score=score_result["total_score"],
            score_breakdown=score_result["breakdown"],
            ats_score=ats_result["ats_score"],
            missing_keywords=ats_result["missing_keywords"],
            suggestions=suggestions,
        )
    finally:
        # Clean up uploaded file after processing (don't keep raw resumes on disk)
        if os.path.exists(filepath):
            os.remove(filepath)

    return redirect(url_for("dashboard", analysis_id=analysis_id))


@app.route("/dashboard/<int:analysis_id>")
def dashboard(analysis_id):
    analysis = db.get_analysis(analysis_id)
    if analysis is None:
        flash("Analysis not found.")
        return redirect(url_for("index"))
    return render_template("dashboard.html", analysis=analysis)


@app.route("/history")
def history():
    records = db.get_history()
    return render_template("history.html", records=records)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
