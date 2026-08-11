# GitHub Team Workflow

## Repository setup

One teammate creates the GitHub repository and adds the other as a collaborator.

## Clone

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd SmartPlacement_DBMS
```

## Create your branch

Ritesh:
```bash
git checkout -b ritesh-backend
```

Krishan:
```bash
git checkout -b krishan-ui
```

## Daily workflow

Before starting:
```bash
git checkout main
git pull origin main
git checkout YOUR_BRANCH
git merge main
```

After making a small working change:
```bash
git add .
git commit -m "Add student registration"
git push -u origin YOUR_BRANCH
```

Then open a Pull Request on GitHub and merge it after checking the code.

## Recommended commit progression

Do NOT create fake commits just to increase the graph. Make real small changes.

1. `Initial project structure`
2. `Create database schema`
3. `Add sample placement data`
4. `Add Flask application setup`
5. `Add student registration`
6. `Add student login`
7. `Build student dashboard`
8. `Add eligibility checking`
9. `Add placement application`
10. `Build admin dashboard`
11. `Add application status updates`
12. `Improve UI and validation`
13. `Add documentation and screenshots`

## Team contribution

Use separate branches and pull requests. This gives GitHub a clear history showing both members actually worked on the project.
