from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from functools import wraps

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "placement.db"

app = Flask(__name__)
app.secret_key = "smart-placement-demo-key"


def get_db():
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    if DB_PATH.exists():
        return
    conn = get_db()
    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    seed = (BASE_DIR / "seed.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.executescript(seed)
    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        course = request.form["course"].strip()
        cgpa = request.form["cgpa"]
        skills = request.form["skills"].strip()
        graduation_year = request.form["graduation_year"]

        try:
            conn = get_db()
            conn.execute("""
                INSERT INTO students
                (name, email, password, course, cgpa, skills, graduation_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, password, course, cgpa, skills, graduation_year))
            conn.commit()
            conn.close()
            flash("Registration successful. Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists or input is invalid.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Simple demo admin account.
        if email == "admin@smartplacement.com" and password == "admin123":
            session["user_id"] = 0
            session["user_name"] = "Placement Admin"
            session["role"] = "admin"
            return redirect(url_for("admin"))

        conn = get_db()
        student = conn.execute(
            "SELECT * FROM students WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()
        conn.close()

        if student:
            session["user_id"] = student["student_id"]
            session["user_name"] = student["name"]
            session["role"] = "student"
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("role") == "admin":
        return redirect(url_for("admin"))

    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (session["user_id"],)
    ).fetchone()

    jobs = conn.execute("""
        SELECT jobs.*, companies.name AS company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.deadline
    """).fetchall()

    applications = conn.execute("""
        SELECT applications.*, jobs.role, companies.name AS company_name
        FROM applications
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        WHERE applications.student_id = ?
        ORDER BY applications.application_id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    # Beginner-friendly eligibility rule:
    # CGPA must meet the company's minimum and at least one listed skill
    # should match when required skills are provided.
    student_skills = {s.strip().lower() for s in student["skills"].split(",") if s.strip()}
    eligible_jobs = []
    for job in jobs:
        required = {s.strip().lower() for s in job["required_skills"].split(",") if s.strip()}
        skill_ok = not required or bool(student_skills.intersection(required))
        if student["cgpa"] >= job["min_cgpa"] and skill_ok:
            eligible_jobs.append(job)

    return render_template(
        "dashboard.html",
        student=student,
        jobs=jobs,
        eligible_jobs=eligible_jobs,
        applications=applications
    )


@app.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id):
    if session.get("role") != "student":
        return redirect(url_for("admin"))

    conn = get_db()
    job = conn.execute("""
        SELECT jobs.*, companies.name AS company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.company_id
        WHERE jobs.job_id = ?
    """, (job_id,)).fetchone()
    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not job:
        flash("Job not found.")
        conn.close()
        return redirect(url_for("dashboard"))

    student_skills = {s.strip().lower() for s in student["skills"].split(",") if s.strip()}
    required = {s.strip().lower() for s in job["required_skills"].split(",") if s.strip()}
    skill_ok = not required or bool(student_skills.intersection(required))

    if student["cgpa"] < job["min_cgpa"] or not skill_ok:
        flash("You are not eligible for this drive.")
    else:
        try:
            conn.execute(
                "INSERT INTO applications (student_id, job_id) VALUES (?, ?)",
                (student["student_id"], job_id)
            )
            conn.commit()
            flash("Application submitted successfully.")
        except sqlite3.IntegrityError:
            flash("You have already applied for this job.")

    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/admin")
@login_required
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()
    stats = {
        "students": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "companies": conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
        "jobs": conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
        "applications": conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0],
        "selected": conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status = 'Selected'"
        ).fetchone()[0],
    }

    applications = conn.execute("""
        SELECT applications.application_id,
               students.name AS student_name,
               companies.name AS company_name,
               jobs.role,
               applications.status
        FROM applications
        JOIN students ON applications.student_id = students.student_id
        JOIN jobs ON applications.job_id = jobs.job_id
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY applications.application_id DESC
    """).fetchall()

    companies = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
    jobs = conn.execute("""
        SELECT jobs.*, companies.name AS company_name
        FROM jobs
        JOIN companies ON jobs.company_id = companies.company_id
        ORDER BY jobs.deadline
    """).fetchall()
    conn.close()

    return render_template(
        "admin.html",
        stats=stats,
        applications=applications,
        companies=companies,
        jobs=jobs
    )


@app.route("/admin/company", methods=["POST"])
@login_required
def add_company():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO companies (name, location, industry) VALUES (?, ?, ?)",
            (request.form["name"], request.form["location"], request.form["industry"])
        )
        conn.commit()
        flash("Company added.")
    except sqlite3.IntegrityError:
        flash("Company already exists.")
    conn.close()
    return redirect(url_for("admin"))


@app.route("/admin/job", methods=["POST"])
@login_required
def add_job():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()
    conn.execute("""
        INSERT INTO jobs
        (company_id, role, package_lpa, min_cgpa, required_skills, deadline)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form["company_id"],
        request.form["role"],
        request.form["package_lpa"],
        request.form["min_cgpa"],
        request.form["required_skills"],
        request.form["deadline"]
    ))
    conn.commit()
    conn.close()
    flash("Job drive added.")
    return redirect(url_for("admin"))


@app.route("/admin/application/<int:application_id>/status", methods=["POST"])
@login_required
def update_status(application_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form["status"]
    if status not in {"Applied", "Shortlisted", "Rejected", "Selected"}:
        flash("Invalid status.")
        return redirect(url_for("admin"))

    conn = get_db()
    conn.execute(
        "UPDATE applications SET status = ? WHERE application_id = ?",
        (status, application_id)
    )
    conn.commit()
    conn.close()
    flash("Application status updated.")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
