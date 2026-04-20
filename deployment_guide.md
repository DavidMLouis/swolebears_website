# Swolé Bears Deployment Guide

Congratulations on finishing the website! To make the site available on the public internet and connect your custom domain from Namecheap, you need a hosting provider (also known as a platform or server).

Since you are running a **Django (Python)** application that uses a local SQLite database, there are two highly recommended approaches depending on your exact needs and technical comfort.

---

## Option 1: Render (Recommended for Modern Workflows)

[Render](https://render.com) is currently the most popular modern hosting platform for Django. It syncs directly with GitHub, meaning every time you push code, it automatically updates your live site. 

**Pros:** Modern, handles HTTPS automatically, clean dashboard, scaling is easy.
**Cons:** The free tier sleeps after 15 minutes of inactivity (paid starts at $7/mo).

### What we need to change in the code for Render:
To deploy on Render, we need a couple of small tweaks to your project:
1. **Add `gunicorn`**: A production server to run Django (since `manage.py runserver` is only for local dev).
2. **Add `whitenoise`**: To serve your static files (CSS, images) in production.
3. **Database**: Render's free tier provides a Postgres database that we can swap SQLite out for (or you can use a "Render Disk" to keep SQLite). 

### How to Host & Connect Namecheap:
1. Push this project folder to a repository on **GitHub**.
2. Create an account on Render and select **"New Web Service"**.
3. Connect your GitHub repository.
4. Set the Build Command to `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`.
5. Set the Start Command to `gunicorn swolebears.wsgi:application`.
6. Once deployed, Render will give you a `.onrender.com` URL. Under your service **Settings -> Custom Domains**, add your Namecheap domain (e.g., `swolebears.com`).
7. Render will provide you with DNS records (typically a `CNAME` or `A` record). 
8. Go to your **Namecheap Dashboard -> Domain List -> Advanced DNS**, and paste those records there. Render will automatically issue an SSL certificate so your site has `https://`.

---

## Option 2: PythonAnywhere (Easiest for SQLite Django)

[PythonAnywhere](https://www.pythonanywhere.com) is a great host specifically designed for Python apps. 

**Pros:** Keeps everything very similar to your local setup (supports SQLite directly), free tier available for `.pythonanywhere.com` domains.
**Cons:** To use a custom domain (like yours from Namecheap), you must upgrade to the "Hacker" plan which is $5/month. Manual deployment (no auto-sync from GitHub on basic plans).

### What we need to change in the code:
**Nothing!** Your current setup will essentially work out-of-the-box on PythonAnywhere.

### How to Host & Connect Namecheap:
1. Create a PythonAnywhere account and upgrade to the $5/mo plan to use custom domains.
2. Under the **Web** tab, click **Add a new web app** and specify your custom domain (e.g., `www.swolebears.com`).
3. Select **Manual configuration (including virtualenvs)** and choose your Python version.
4. Upload your project folder as a ZIP file in the **Files** tab and extract it.
5. In the **Web** tab, edit the **WSGI configuration file** to point to your `swolebears.settings`.
6. PythonAnywhere will give you a CNAME target (e.g., `webapp-123456.pythonanywhere.com`).
7. Go to **Namecheap Dashboard -> Domain List -> Advanced DNS** and add a `CNAME Record` for `www` pointing to the PythonAnywhere target.

---

> [!TIP]
> **My Recommendation:** I highly recommend **Render** (or a similar platform like **Railway**). While it requires a few extra lines of configuration (which I can add for you instantly!), it creates a much better, professional workflow, especially if you plan to update the site often.

## How do you want to proceed?

If you'd like to use **Render** (or any other modern platform):
1. **Let me know**, and I will instantly run the commands to update your `requirements.txt` and `settings.py` for production.
2. Put the code on GitHub (if it isn't already).
3. Connect it to the hosting platform.

If you don't use Git/GitHub, we can stick to **PythonAnywhere** or you can just Zip the project and drag it to a server!
