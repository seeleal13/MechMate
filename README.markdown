# MechMate

![MechMate Logo](static/logo.png)

A Flask-based web app for tracking vehicle maintenance logs, built for the Summer of Making hackclub event. Manage your car’s repair history with ease!

## Features
- **Web App**: Register, log in, and manage vehicles/repair logs via a browser.
- **Vehicle & Log Management**: Add/edit/delete vehicles and logs with custom dates.
- **Stylish Design**: Light yellow (#F6F5F1) and black-gray (#171612) theme with a 900px logo.
- **Responsive UI**: Clean tables for logs and dynamic dropdowns for vehicle selection.

## 💻 Software Stack
- Python 3.11+
- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Flask-WTF 1.2.1

## 📁 Project Structure
```
MechMate/
│
├── app.py              # Main Flask app
├── static/             # Static files (logo.png)
├── templates/          # HTML templates (home, register, login, etc.)
├── requirements.txt    # Dependencies
├── .gitignore         # Git config file
└── README.md          # This file
```

## 🚀 How to Run

### Option 1: Run Locally in Your Code Editor
1. Clone the repository:
   ```bash
   git clone https://github.com/Seeleal13/MechMate.git
   cd MechMate
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app (creates `site.db` automatically):
   ```bash
   python3 app.py
   ```
5. Open `http://localhost:5000` in your browser.

💡 On some systems, use `python` instead of `python3`.

### Option 2: Run on PythonAnywhere
Visit the deployed app at: [https://seeleal13.pythonanywhere.com/](https://seeleal13.pythonanywhere.com/)

## My Journey
MechMate was my passion project for the Summer of Making hackclub event. I built a sleek Flask app with custom log dates, vehicle/log management, and a light yellow/black-gray theme. Deploying to PythonAnywhere was a hurdle—`sqlite3.OperationalError` issues with `/tmp/site.db` drove me nuts! After fixing database initialization, it’s live, though the dashboard occasionally lags or misses vehicles.