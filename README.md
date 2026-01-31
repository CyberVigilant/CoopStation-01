# Coop Station 🚀
University Co-op Opportunity Platform built with Django.

This guide explains how to run the project locally on **Windows** and **macOS** after downloading the project as a ZIP file or cloning it.

---

## 📦 Requirements

Before starting, make sure you have:

- Python 3.10 or higher  
- pip (comes with Python)  
- pipenv  

Check Python version:

```bash
python --version
```

or

```bash
python3 --version
```

---

## 🔧 Install pipenv (One Time)

### Windows

```bash
pip install pipenv
```

### macOS

```bash
python3 -m pip install --user pipenv
```

Verify installation:

```bash
pipenv --version
```

---

## 📥 Download Project

### Option 1 (ZIP)

1. Click **Code → Download ZIP**
2. Extract the folder
3. Open the folder in VS Code

### Option 2 (Git)

```bash
git clone <repo-url>
```

---

## ⚙️ Setup Project

Open terminal inside project folder.

Install dependencies:

```bash
pipenv install
```

Activate environment:

```bash
pipenv shell
```

---

## ▶️ Run Server

```bash
python manage.py runserver
```

or

```bash
pipenv run python manage.py runserver
```

---

## 🌐 Open in Browser

```
http://127.0.0.1:8000/
```

---

## 🗃 Database Setup (First Time Only)

```bash
python manage.py migrate
```

(Optional) Create admin user:

```bash
python manage.py createsuperuser
```

---

## 🛑 Common Errors

### No module named django

```bash
pipenv shell
```

### python not found

```bash
python3 manage.py runserver
```

---

## 🚫 Do NOT Commit These Files

```
__pycache__/
db.sqlite3
.env
```

---

## 👥 Team Workflow

Each developer:

- Downloads project  
- Runs `pipenv install`  
- Runs server locally  

Virtual environments are NOT shared.

---

## 📫 Support

If setup fails, send a screenshot of the error in the group chat.

Happy coding 🎉
