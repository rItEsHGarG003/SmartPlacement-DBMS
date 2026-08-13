PRAGMA foreign_keys = ON;


-- ============================================
-- STUDENTS
-- ============================================

INSERT INTO students
    (name, email, password, course, cgpa, graduation_year)
VALUES
    ('Ritesh', 'ritesh@student.com', '1234', 'MCA', 8.2, 2027),

    ('Demo Student', 'student@student.com', '1234', 'MCA', 7.1, 2027);


-- ============================================
-- COMPANIES
-- ============================================

INSERT INTO companies
    (name, location, industry)
VALUES
    ('TechNova', 'Hyderabad', 'Software'),

    ('DataBridge', 'Bengaluru', 'Analytics'),

    ('CloudPeak', 'Pune', 'Cloud Technology');


-- ============================================
-- JOBS
-- ============================================

INSERT INTO jobs
    (company_id, role, package_lpa, min_cgpa, deadline)
VALUES
    (1, 'Software Developer Intern', 8.0, 7.0, '2026-09-15'),

    (2, 'Data Analyst Intern', 7.0, 7.5, '2026-09-20'),

    (3, 'Cloud Intern', 6.5, 6.5, '2026-09-25');


-- ============================================
-- SKILLS
-- ============================================

INSERT INTO skills
    (skill_name)
VALUES
    ('C++'),

    ('Python'),

    ('DBMS'),

    ('DSA'),

    ('SQL');


-- ============================================
-- STUDENT SKILLS
-- ============================================

-- Ritesh:
-- C++, Python, DBMS, DSA

INSERT INTO student_skills
    (student_id, skill_id)
VALUES
    (1, 1),  -- C++
    (1, 2),  -- Python
    (1, 3),  -- DBMS
    (1, 4);  -- DSA


-- Demo Student:
-- Python, SQL

INSERT INTO student_skills
    (student_id, skill_id)
VALUES
    (2, 2),  -- Python
    (2, 5);  -- SQL


-- ============================================
-- JOB SKILLS
-- ============================================

-- Software Developer Intern:
-- C++, Python

INSERT INTO job_skills
    (job_id, skill_id)
VALUES
    (1, 1),  -- C++
    (1, 2);  -- Python


-- Data Analyst Intern:
-- Python, SQL

INSERT INTO job_skills
    (job_id, skill_id)
VALUES
    (2, 2),  -- Python
    (2, 5);  -- SQL


-- Cloud Intern:
-- Python

INSERT INTO job_skills
    (job_id, skill_id)
VALUES
    (3, 2);  -- Python