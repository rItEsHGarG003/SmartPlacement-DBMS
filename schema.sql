PRAGMA foreign_keys = ON;

-- Drop tables in dependency order
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS job_skills;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS students;


-- ============================================
-- STUDENTS TABLE
-- ============================================

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    course TEXT NOT NULL,
    cgpa REAL NOT NULL CHECK(cgpa >= 0 AND cgpa <= 10),
    graduation_year INTEGER NOT NULL
);


-- ============================================
-- COMPANIES TABLE
-- ============================================

CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    location TEXT,
    industry TEXT
);


-- ============================================
-- JOBS TABLE
-- ============================================

CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    package_lpa REAL NOT NULL CHECK(package_lpa >= 0),
    min_cgpa REAL NOT NULL CHECK(min_cgpa >= 0 AND min_cgpa <= 10),
    deadline TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);


-- ============================================
-- SKILLS TABLE
-- ============================================

CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE
);


-- ============================================
-- STUDENT_SKILLS TABLE
-- ============================================

CREATE TABLE student_skills (
    student_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,

    PRIMARY KEY (student_id, skill_id),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
        ON DELETE CASCADE
);


-- ============================================
-- JOB_SKILLS TABLE
-- ============================================

CREATE TABLE job_skills (
    job_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,

    PRIMARY KEY (job_id, skill_id),

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
        ON DELETE CASCADE
);


-- ============================================
-- APPLICATIONS TABLE
-- ============================================

CREATE TABLE applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,

    status TEXT NOT NULL DEFAULT 'Applied'
        CHECK(status IN (
            'Applied',
            'Shortlisted',
            'Rejected',
            'Selected'
        )),

    -- A student can apply to a particular job only once
    UNIQUE (student_id, job_id),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE
);