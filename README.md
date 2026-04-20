# Swolé Bears Landing Page

This is the production-ready Python Django application for the Swolé Bears landing page, configured for maximum conversion and robust email capture.

## Setup Requirements

1. **Python 3.10+**
2. **Virtual Environment** (recommended)

## Quick Start

1. **Create Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and replace placeholders
   ```

4. **Initialize Database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run Server:**
   ```bash
   python manage.py runserver
   ```
   Visit `http://localhost:8000`

## Features

- **High-Converting UX**: Modern, fitness-centric design using Tailwind CSS.
- **Dual-Storage Signups**: Form submissions save securely to the Django SQLite database AND instantly sync to a designated Google Sheet.
- **Fail-Safe Design**: If the Google Sheets API fails (e.g., credentials expire), the app silently catches the error, saves the lead to the DB, and shows the user a "Success" message to maintain conversion momentum.
- **Spam Protection**: Invisible honeypot fields on all forms block automated bots without impacting user friction.
- **UTM Tracking**: UTM parameters in the URL are parsed and persist through the session, attaching to the lead when they sign up.

## External Integrations

### Google Sheets API Setup

The landing page captures emails and directly pushes them to a Google Sheet.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new Project or select an existing one.
3. Search for "Google Sheets API" and enable it.
4. Go to **Credentials**, click **Create Credentials**, and select **Service Account**.
5. Once created, go to the Service Account details > **Keys** > **Add Key** > **Create new key** (JSON).
6. Download the `credentials.json` file and place it in the project root.
7. Open the JSON file to find the `client_email`.
8. Create a new Google Sheet. Click **Share** and add that `client_email` as an **Editor**.
9. Grab your spreadsheet ID from the URL (e.g., `https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit`) and place it in the `.env` file for `GOOGLE_SHEET_ID`.

## Content Editing

- **Copywriting**: All text resides in the HTML templates found at `/templates/partials/`.
- **CSS Formatting**: Powered dynamically via Tailwind Play CDN defined in `templates/base.html`. The brand colors (reds, darks) are configured there. Overrides are in `static/css/styles.css`.
- **Images**: Drop your product and founder images into `/static/images/` and ensure the filenames align with the references in the HTML files. I have added placeholders (`product-hero.png`, `lifestyle-gym.jpg`, `product-bag.jpg`, `founder.jpg`).

## Deployment

This app is production-ready.
1. Change `DJANGO_DEBUG` to `False` in `.env`.
2. Generate a secure `DJANGO_SECRET_KEY` and add it to `.env`.
3. Update `DJANGO_ALLOWED_HOSTS` to contain your domain (e.g., `swolebears.com`).
4. Execute `python manage.py collectstatic` to gather CSS/JS/Images.
5. Deploy using Gunicorn or AWS Elastic Beanstalk / Heroku following standard Django buildpacks.
