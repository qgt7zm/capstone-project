# Gamification Learning Tool

## Description

Gamification is growing more popular by the day, with more and more industries and sectors using the power of
play to drive increased productivity and satisfaction.
But does gamification really work, or is it more hype than truth?

This application is an interactive gamification learning tool for educators with a user-friendly interface created
in the Django web framework.
Simply input your classroom needs, and the website will recommend a solution for you, backed by results from published
and peer-reviewed scientific studies.

Created for BSCS Capstone project at UVA.

## Instructions

### Development Environment

1. Clone or download this repository using the GitHub website, desktop app, or git command line.
2. (**Recommended**) Create a Python virtual environment using `python3 -m venv .venv`.
3. (**Recommended**) Activate the virtual environment using `source .venv/bin/activate` (Unix)
   or `.venv\bin\activate.bat`.
4. Install the required Python packages with `pip3 install -r requirements.txt`.

### Database

1. (_Optional_) Set your production database in [settings.py](mysite/settings.py) under `DATABASES`.
2. Create or migrate your database by running `python3 manage.py migrate`.

### Environment Variables

1. Generate a Django secret key by running `python3 gen_secret_key.py`.
2. Copy or rename [.env.blank](.env.blank) to `.env` and paste your secret key there.
3. Run the local development server with `python3 manage.py runserver 8000`.
4. Access the website on a web browser at http://127.0.0.1:8000/.