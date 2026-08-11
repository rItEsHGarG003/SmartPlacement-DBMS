INSERT INTO students (name, email, password, course, cgpa, skills, graduation_year)
VALUES
('Ritesh', 'ritesh@student.com', '1234', 'MCA', 8.2, 'C++, Python, DBMS, DSA', 2027),
('Demo Student', 'student@student.com', '1234', 'MCA', 7.1, 'Python, SQL', 2027);

INSERT INTO companies (name, location, industry)
VALUES
('TechNova', 'Hyderabad', 'Software'),
('DataBridge', 'Bengaluru', 'Analytics'),
('CloudPeak', 'Pune', 'Cloud Technology');

INSERT INTO jobs (company_id, role, package_lpa, min_cgpa, required_skills, deadline)
VALUES
(1, 'Software Developer Intern', 8.0, 7.0, 'C++, Python', '2026-09-15'),
(2, 'Data Analyst Intern', 7.0, 7.5, 'Python, SQL', '2026-09-20'),
(3, 'Cloud Intern', 6.5, 6.5, 'Python', '2026-09-25');
