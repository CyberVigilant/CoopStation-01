# Coop Station 🚀
University Co-op Opportunity Platform built with Django.

This guide explains how to run the project locally on Windows and macOS after downloading the project as a ZIP file or cloning it.

---

📦 REQUIREMENTS

Before starting, make sure you have:

- Python 3.10 or higher
- pip (comes with Python)
- pipenv

Check Python version:

python --version
or
python3 --version

---

🔧 INSTALL PIPENV (ONE TIME)

Windows:
pip install pipenv

macOS:
python3 -m pip install --user pipenv

Verify installation:
pipenv --version

---

📥 DOWNLOAD PROJECT

Option 1 (ZIP):
1. Click Code → Download ZIP
2. Extract the folder
3. Open the folder in VS Code

Option 2 (Git):
git clone <repo-url>

---

⚙️ SETUP PROJECT

Open terminal inside the project folder.

Install dependencies:
pipenv install

Activate environment:
pipenv shell

---

▶️ RUN SERVER

python manage.py runserver

OR

pipenv run python manage.py runserver

---

🌐 OPEN IN BROWSER

http://127.0.0.1:8000/

---

🗃 DATABASE SETUP (FIRST TIME ONLY)

python manage.py migrate

(Optional) Create admin user:
python manage.py createsuperuser

---

🛑 COMMON ERRORS

"No module named django"
You forgot to activate pipenv:
pipenv shell

"python not found"
Try:
python3 manage.py runserver

---

🚫 DO NOT COMMIT THESE FILES

__pycache__/
db.sqlite3
.env

---

👥 TEAM WORKFLOW

Each developer:
- Downloads project
- Runs pipenv install
- Runs server locally

Virtual environments are NOT shared.

---

📫 SUPPORT

If setup fails, send a screenshot of the error in the group chat.

Happy coding 🎉
