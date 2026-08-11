PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    course TEXT NOT NULL,
    cgpa REAL NOT NULL CHECK(cgpa >= 0 AND cgpa <= 10),
    skills TEXT DEFAULT '',
    graduation_year INTEGER NOT NULL
);

CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    location TEXT,
    industry TEXT
);

CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    package_lpa REAL NOT NULL CHECK(package_lpa >= 0),
    min_cgpa REAL NOT NULL CHECK(min_cgpa >= 0 AND min_cgpa <= 10),
    required_skills TEXT DEFAULT '',
    deadline TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

CREATE TABLE applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Applied'
        CHECK(status IN ('Applied', 'Shortlisted', 'Rejected', 'Selected')),
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, job_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);
