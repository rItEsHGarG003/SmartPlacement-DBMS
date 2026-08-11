# SmartPlacement Project Plan

## Scope
Keep the project medium-sized. Do not add AI, chatbots, payment systems, complex deployment, or unnecessary APIs.

## Modules

1. Authentication
2. Student profile
3. Company management
4. Placement drive management
5. Eligibility checking
6. Application tracking
7. Admin statistics

## Database relationships

```text
COMPANY 1 ---- N JOB
STUDENT 1 ---- N APPLICATION N ---- 1 JOB
```

Applications acts as the bridge between students and jobs.

## Suggested viva explanation

### Problem
Students often have to check many placement notices and manually determine whether they meet eligibility criteria.

### Solution
SmartPlacement stores student information and placement drives in a relational database and checks basic eligibility automatically.

### DBMS part
The project uses separate tables for students, companies, jobs and applications. Foreign keys connect the tables, while a unique constraint prevents duplicate applications.

### Why SQLite?
It is easy to install and enough for a classroom project. The schema can later be moved to MySQL without changing the basic relational design.

## Future scope
Keep these as future scope only; do not implement unless the professor asks:
- Email notifications
- Resume upload
- Advanced analytics
- MySQL deployment
- Role-based company login
