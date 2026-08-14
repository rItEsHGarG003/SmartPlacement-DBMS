from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from functools import wraps


# ============================================
# PROJECT PATHS
# ============================================

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "placement.db"


# ============================================
# FLASK APP
# ============================================

app = Flask(__name__)
app.secret_key = "smart-placement-demo-key"


# ============================================
# DATABASE CONNECTION
# ============================================

def get_db():
    DB_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================
# DATABASE INITIALIZATION
# ============================================

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


# ============================================
# LOGIN DECORATOR
# ============================================

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapper


# ============================================
# HELPER: ADD STUDENT SKILLS
# ============================================

def add_student_skills(conn, student_id, skills_text):

    skills = {
        skill.strip()
        for skill in skills_text.split(",")
        if skill.strip()
    }

    for skill_name in skills:

        # Add skill if it does not already exist
        conn.execute(
            """
            INSERT OR IGNORE INTO skills (skill_name)
            VALUES (?)
            """,
            (skill_name,)
        )

        # Get skill ID
        skill = conn.execute(
            """
            SELECT skill_id
            FROM skills
            WHERE skill_name = ?
            """,
            (skill_name,)
        ).fetchone()

        # Connect student with skill
        conn.execute(
            """
            INSERT OR IGNORE INTO student_skills
            (student_id, skill_id)
            VALUES (?, ?)
            """,
            (student_id, skill["skill_id"])
        )


# ============================================
# HELPER: ADD JOB SKILLS
# ============================================

def add_job_skills(conn, job_id, skills_text):

    skills = {
        skill.strip()
        for skill in skills_text.split(",")
        if skill.strip()
    }

    for skill_name in skills:

        # Add skill if it does not already exist
        conn.execute(
            """
            INSERT OR IGNORE INTO skills (skill_name)
            VALUES (?)
            """,
            (skill_name,)
        )

        # Get skill ID
        skill = conn.execute(
            """
            SELECT skill_id
            FROM skills
            WHERE skill_name = ?
            """,
            (skill_name,)
        ).fetchone()

        # Connect job with skill
        conn.execute(
            """
            INSERT OR IGNORE INTO job_skills
            (job_id, skill_id)
            VALUES (?, ?)
            """,
            (job_id, skill["skill_id"])
        )


# ============================================
# HOME
# ============================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ============================================
# REGISTER
# ============================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        course = request.form["course"].strip()
        cgpa = request.form["cgpa"]
        skills_text = request.form["skills"].strip()
        graduation_year = request.form["graduation_year"]

        try:

            conn = get_db()

            # Create student
            cursor = conn.execute(
                """
                INSERT INTO students
                (name, email, password, course, cgpa, graduation_year)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    password,
                    course,
                    cgpa,
                    graduation_year
                )
            )

            student_id = cursor.lastrowid

            # Add student's skills
            add_student_skills(
                conn,
                student_id,
                skills_text
            )

            conn.commit()
            conn.close()

            flash("Registration successful. Please login.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("Email already exists or input is invalid.")

    return render_template("register.html")


# ============================================
# LOGIN
# ============================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Simple demo admin account
        if (
            email == "admin@smartplacement.com"
            and password == "admin123"
        ):

            session["user_id"] = 0
            session["user_name"] = "Placement Admin"
            session["role"] = "admin"

            return redirect(url_for("admin"))

        # Student login
        conn = get_db()

        student = conn.execute(
            """
            SELECT *
            FROM students
            WHERE email = ?
            AND password = ?
            """,
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


# ============================================
# LOGOUT
# ============================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================
# STUDENT DASHBOARD
# ============================================

@app.route("/dashboard")
@login_required
def dashboard():

    # Admin should go to admin dashboard
    if session.get("role") == "admin":
        return redirect(url_for("admin"))

    conn = get_db()

    # Get current student
    student = conn.execute(
        """
        SELECT *
        FROM students
        WHERE student_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # Get all jobs
    jobs = conn.execute(
        """
        SELECT
            jobs.*,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.company_id
        ORDER BY jobs.deadline
        """
    ).fetchall()

    # Get student's applications
    applications = conn.execute(
        """
        SELECT
            applications.*,
            jobs.role,
            companies.name AS company_name
        FROM applications
        JOIN jobs
            ON applications.job_id = jobs.job_id
        JOIN companies
            ON jobs.company_id = companies.company_id
        WHERE applications.student_id = ?
        ORDER BY applications.application_id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    # ========================================
    # ELIGIBILITY CHECK
    # ========================================

    eligible_jobs = []

    for job in jobs:

        # Check CGPA
        cgpa_ok = student["cgpa"] >= job["min_cgpa"]

        # Count required skills that the student has
        matching_skills = conn.execute(
            """
            SELECT COUNT(*)
            FROM job_skills js
            JOIN student_skills ss
                ON js.skill_id = ss.skill_id
            WHERE js.job_id = ?
            AND ss.student_id = ?
            """,
            (
                job["job_id"],
                student["student_id"]
            )
        ).fetchone()[0]

        # Count total required skills
        required_skills = conn.execute(
            """
            SELECT COUNT(*)
            FROM job_skills
            WHERE job_id = ?
            """,
            (job["job_id"],)
        ).fetchone()[0]

        # Eligibility rule:
        # 1. Student must satisfy minimum CGPA
        # 2. Student must have all required skills
        skills_ok = (
            matching_skills == required_skills
        )

        if cgpa_ok and skills_ok:
            eligible_jobs.append(job)

    conn.close()

    return render_template(
        "dashboard.html",
        student=student,
        jobs=jobs,
        eligible_jobs=eligible_jobs,
        applications=applications
    )


# ============================================
# APPLY FOR JOB
# ============================================

@app.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id):

    # Only students can apply
    if session.get("role") != "student":
        return redirect(url_for("admin"))

    conn = get_db()

    # Get job
    job = conn.execute(
        """
        SELECT
            jobs.*,
            companies.name AS company_name
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.company_id
        WHERE jobs.job_id = ?
        """,
        (job_id,)
    ).fetchone()

    # Get student
    student = conn.execute(
        """
        SELECT *
        FROM students
        WHERE student_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # Job does not exist
    if not job:

        flash("Job not found.")
        conn.close()

        return redirect(url_for("dashboard"))

    # ========================================
    # CHECK CGPA
    # ========================================

    cgpa_ok = (
        student["cgpa"] >= job["min_cgpa"]
    )

    # ========================================
    # CHECK SKILLS
    # ========================================

    matching_skills = conn.execute(
        """
        SELECT COUNT(*)
        FROM job_skills js
        JOIN student_skills ss
            ON js.skill_id = ss.skill_id
        WHERE js.job_id = ?
        AND ss.student_id = ?
        """,
        (
            job_id,
            student["student_id"]
        )
    ).fetchone()[0]

    required_skills = conn.execute(
        """
        SELECT COUNT(*)
        FROM job_skills
        WHERE job_id = ?
        """,
        (job_id,)
    ).fetchone()[0]

    skills_ok = (
        matching_skills == required_skills
    )

    # ========================================
    # FINAL ELIGIBILITY CHECK
    # ========================================

    if not cgpa_ok or not skills_ok:

        flash("You are not eligible for this drive.")
        conn.close()

        return redirect(url_for("dashboard"))

    # ========================================
    # APPLY
    # ========================================

    try:

        conn.execute(
            """
            INSERT INTO applications
            (student_id, job_id)
            VALUES (?, ?)
            """,
            (
                student["student_id"],
                job_id
            )
        )

        conn.commit()

        flash("Application submitted successfully.")

    except sqlite3.IntegrityError:

        flash("You have already applied for this job.")

    conn.close()

    return redirect(url_for("dashboard"))


# ============================================
# ADMIN DASHBOARD
# ============================================

@app.route("/admin")
@login_required
def admin():

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    # ========================================
    # STATISTICS
    # ========================================

    total_students = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        """
    ).fetchone()[0]

    total_companies = conn.execute(
        """
        SELECT COUNT(*)
        FROM companies
        """
    ).fetchone()[0]

    total_jobs = conn.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        """
    ).fetchone()[0]

    total_applications = conn.execute(
        """
        SELECT COUNT(*)
        FROM applications
        """
    ).fetchone()[0]

    selected_applications = conn.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE status = 'Selected'
        """
    ).fetchone()[0]

    # Count unique students who have been selected.
    # This is used for placement percentage.
    placed_students = conn.execute(
        """
        SELECT COUNT(DISTINCT student_id)
        FROM applications
        WHERE status = 'Selected'
        """
    ).fetchone()[0]

    # Placement percentage:
    # Number of uniquely placed students / total students * 100
    if total_students > 0:
        placement_percentage = round(
            (placed_students / total_students) * 100,
            2
        )
    else:
        placement_percentage = 0

    stats = {
        "students": total_students,
        "companies": total_companies,
        "jobs": total_jobs,
        "applications": total_applications,
        "selected": selected_applications,
        "placed_students": placed_students,
        "placement_percentage": placement_percentage
    }

    # ========================================
    # APPLICATIONS
    # ========================================

    applications = conn.execute(
        """
        SELECT
            applications.application_id,
            students.name AS student_name,
            companies.name AS company_name,
            jobs.role,
            applications.applied_at,
            applications.status
        FROM applications
        JOIN students
            ON applications.student_id = students.student_id
        JOIN jobs
            ON applications.job_id = jobs.job_id
        JOIN companies
            ON jobs.company_id = companies.company_id
        ORDER BY applications.application_id DESC
        """
    ).fetchall()

    # ========================================
    # COMPANIES
    # ========================================

    companies = conn.execute(
        """
        SELECT *
        FROM companies
        ORDER BY name
        """
    ).fetchall()

    # ========================================
    # JOBS
    # ========================================

    jobs = conn.execute(
        """
        SELECT
            jobs.job_id,
            jobs.company_id,
            jobs.role,
            jobs.package_lpa,
            jobs.min_cgpa,
            jobs.deadline,
            companies.name AS company_name,
            GROUP_CONCAT(
                skills.skill_name,
                ', '
            ) AS required_skills
        FROM jobs
        JOIN companies
            ON jobs.company_id = companies.company_id
        LEFT JOIN job_skills
            ON jobs.job_id = job_skills.job_id
        LEFT JOIN skills
            ON job_skills.skill_id = skills.skill_id
        GROUP BY
            jobs.job_id,
            jobs.company_id,
            jobs.role,
            jobs.package_lpa,
            jobs.min_cgpa,
            jobs.deadline,
            companies.name
        ORDER BY jobs.deadline
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        stats=stats,
        applications=applications,
        companies=companies,
        jobs=jobs
    )


# ============================================
# ADD COMPANY
# ============================================

@app.route("/admin/company", methods=["POST"])
@login_required
def add_company():

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:

        conn.execute(
            """
            INSERT INTO companies
            (name, location, industry)
            VALUES (?, ?, ?)
            """,
            (
                request.form["name"],
                request.form["location"],
                request.form["industry"]
            )
        )

        conn.commit()

        flash("Company added.")

    except sqlite3.IntegrityError:

        flash("Company already exists.")

    conn.close()

    return redirect(url_for("admin"))


# ============================================
# ADD JOB
# ============================================

@app.route("/admin/job", methods=["POST"])
@login_required
def add_job():

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:

        # ====================================
        # CREATE JOB
        # ====================================

        cursor = conn.execute(
            """
            INSERT INTO jobs
            (
                company_id,
                role,
                package_lpa,
                min_cgpa,
                deadline
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.form["company_id"],
                request.form["role"],
                request.form["package_lpa"],
                request.form["min_cgpa"],
                request.form["deadline"]
            )
        )

        job_id = cursor.lastrowid

        # ====================================
        # ADD REQUIRED SKILLS
        # ====================================

        required_skills = request.form[
            "required_skills"
        ].strip()

        add_job_skills(
            conn,
            job_id,
            required_skills
        )

        conn.commit()

        flash("Job drive added.")

    except sqlite3.IntegrityError:

        conn.rollback()

        flash("Unable to add job. Please check the input.")

    conn.close()

    return redirect(url_for("admin"))


# ============================================
# UPDATE APPLICATION STATUS
# ============================================

@app.route(
    "/admin/application/<int:application_id>/status",
    methods=["POST"]
)
@login_required
def update_status(application_id):

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form["status"]

    # Only these statuses are allowed
    if status not in {
        "Applied",
        "Shortlisted",
        "Rejected",
        "Selected"
    }:

        flash("Invalid status.")

        return redirect(url_for("admin"))

    conn = get_db()

    conn.execute(
        """
        UPDATE applications
        SET status = ?
        WHERE application_id = ?
        """,
        (
            status,
            application_id
        )
    )

    conn.commit()
    conn.close()

    flash("Application status updated.")

    return redirect(url_for("admin"))


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":

    initialize_database()

    app.run(debug=True)