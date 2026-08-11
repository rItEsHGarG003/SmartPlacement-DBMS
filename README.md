# SmartPlacement DBMS

A beginner-friendly, medium-level **Placement Management System** built with **Python Flask + SQLite + HTML/CSS**.

## Team
- Ritesh
- Krishan Mohan Tripathi

## Why this project?
The system models a real college placement workflow instead of being only a CRUD demo.

### Main features
- Student registration/login
- Student profile with CGPA and skills
- Company management
- Job/drive creation
- Automatic eligibility checking
- Student application tracking
- Admin dashboard
- Placement statistics
- SQLite relational database with foreign keys
- Simple responsive UI

## Technology
- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- Jinja2

## Project structure

```text
SmartPlacement_DBMS/
│
├── app.py
├── schema.sql
├── seed.sql
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   └── placement.db              # created automatically
│
├── static/
│   └── style.css
│
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── students.html
    ├── companies.html
    ├── jobs.html
    ├── applications.html
    └── admin.html
```

## Run locally

### 1. Create virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install packages
```bash
pip install -r requirements.txt
```

### 3. Start the application
```bash
python app.py
```

Open:
`http://127.0.0.1:5000`

The application creates the database automatically and inserts sample data on first run.

## Demo accounts

Student:
- Email: `ritesh@student.com`
- Password: `1234`

Admin:
- Email: `admin@smartplacement.com`
- Password: `admin123`

## Suggested division of work

### Ritesh
- Database design
- Flask routes
- Application/eligibility logic
- GitHub integration

### Krishan Mohan Tripathi
- HTML templates
- CSS/UI
- Testing
- Documentation and screenshots

Both members should make regular commits so the GitHub history shows genuine progress.

## Important DBMS concepts demonstrated
- Primary keys
- Foreign keys
- One-to-many relationships
- Many-to-many relationship through applications
- Constraints
- JOIN queries
- Aggregate functions
- GROUP BY
- WHERE filtering
- Database normalization
- Transactions
