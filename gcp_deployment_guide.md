# Hosting Django on GCP's "Always Free" Tier

To solve the "cold start" issue you're experiencing on Render's free tier, we can use Google Cloud Platform (GCP). Google offers a generous [Always Free Tier](https://cloud.google.com/free) that includes **one `e2-micro` Compute Engine virtual machine (VM) per month**. 

Unlike Render or Cloud Run which spin down when idle to save resources, a Compute Engine VM is a dedicated server that runs 24/7. This guarantees **zero cold starts** and allows you to use your existing SQLite database without losing data.

Here is the step-by-step walkthrough customized for `swolebears.com`!

## Step 1: Create a GCP Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account and sign up for the free trial (you won't be charged if you stay within the free tier).
3. Click the **Project Dropdown** at the top of the page and select **New Project**. Name it `Swole-Bears-Landing` and click **Create**.

## Step 2: Create the Free Tier VM
You need to be very specific with your settings here to ensure the VM is 100% free according to [Google's Free Tier limits](https://cloud.google.com/free/docs/gcp-free-tier#compute).

1. Go to **Compute Engine > VM instances**.
2. Click **Create Instance**.
3. **Name**: `swolebears-web`.
4. **Region**: You **MUST** select one of these three regions to qualify for the free tier: `us-central1`, `us-east1`, or `us-west1`.
5. **Machine Configuration**: 
   - Series: **E2**
   - Machine type: **e2-micro** (2 vCPU, 1 GB memory)
6. **Boot Disk**: 
   - Click "Change" under Boot Disk.
   - Operating System: **Ubuntu**
   - Version: **Ubuntu 22.04 LTS**
   - Boot disk type: **Standard persistent disk** *(Do NOT use Balanced or SSD)*.
   - Size: **30 GB**.
7. **Firewall**: Check both **Allow HTTP traffic** and **Allow HTTPS traffic**.
8. Click **Create**.

## Step 3: Reserve a Static IP Address
1. Go to **VPC network > IP addresses**.
2. Click **Reserve External Static Address**.
3. Name it `swolebears-ip`.
4. Network Service Tier: **Standard** *(Premium tier costs money!)*.
5. Region: Ensure it matches the region you picked for your VM.
6. Attached to: Select your `swolebears-web` VM.
7. Click **Reserve**. 

## Step 4: Point Namecheap to your New IP
1. Copy the new static IP address.
2. Log in to Namecheap, go to **Advanced DNS** for your domain.
3. Update your **A Record** to point to this new GCP IP address.

## Step 5: Setup the Server Environment
1. Go back to **Compute Engine > VM instances** and click **SSH** to open a terminal in your browser.
2. Update the system and install necessary packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-venv nginx git certbot python3-certbot-nginx -y
   ```

## Step 6: Clone and Configure Your Application
1. Clone your code and enter the directory:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git swolebears_website
   cd swolebears_website
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt gunicorn
   ```
3. Create your `.env` file (since Git ignores it):
   ```bash
   cat << 'EOF' > .env
   # Django Configuration
   DJANGO_SECRET_KEY="<generate-a-new-random-string-here>"
   DJANGO_DEBUG="False"
   DJANGO_ALLOWED_HOSTS="swolebears.com,www.swolebears.com,<your-static-ip>"

   # Google Sheets Configuration
   GOOGLE_SHEETS_CREDENTIALS_FILE="credentials.json"
   GOOGLE_SHEET_ID="<your-actual-spreadsheet-id>"
   GOOGLE_SHEET_WORKSHEET_NAME="Sheet1"
   EOF
   ```
4. Create your `credentials.json` file the same way (pasting your actual key contents):
   ```bash
   cat << 'EOF' > credentials.json
   PASTE_YOUR_ENTIRE_CREDENTIALS_JSON_CONTENT_HERE
   EOF
   ```
5. Run migrations and collect static files:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

## Step 7: Fix Home Directory Permissions
By default, Ubuntu locks down your home folder, which causes Nginx to throw a `502 Bad Gateway` error because it can't read your website files.
Give Nginx "pass-through" permission to your home folder:
```bash
sudo chmod 755 /home/dmlouis
```

## Step 8: Keep the App Running Automatically
Create a `systemd` service so Gunicorn runs automatically even if the VM reboots.
1. Open the service file:
   ```bash
   sudo nano /etc/systemd/system/swolebears.service
   ```
2. Paste this exact configuration:
   ```ini
   [Unit]
   Description=Gunicorn daemon for Swole Bears
   After=network.target

   [Service]
   User=dmlouis
   Group=www-data
   WorkingDirectory=/home/dmlouis/swolebears_website
   Environment="PATH=/home/dmlouis/swolebears_website/venv/bin"
   ExecStart=/home/dmlouis/swolebears_website/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/dmlouis/swolebears_website/swolebears.sock swolebears.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```
3. Start the service:
   ```bash
   sudo systemctl start swolebears
   sudo systemctl enable swolebears
   ```

## Step 9: Configure Nginx and SSL
1. Delete the default Nginx placeholder page so it doesn't hijack your site:
   ```bash
   sudo rm /etc/nginx/sites-enabled/default
   ```
2. Set up your custom Nginx configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/swolebears
   ```
3. Add this configuration block:
   ```nginx
   server {
       listen 80;
       server_name swolebears.com www.swolebears.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /home/dmlouis/swolebears_website;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/home/dmlouis/swolebears_website/swolebears.sock;
       }
   }
   ```
4. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/swolebears /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```
5. Finally, secure the site with HTTPS/SSL:
   ```bash
   sudo certbot --nginx -d swolebears.com -d www.swolebears.com
   ```

## How to Verify You're Staying Free
To ensure you never get a surprise bill:
1. **Set a Budget Alert**: Go to Billing > Budgets & alerts in GCP and create a budget for `$1.00` to email you if it hits `$0.01`.
2. **Double Check Constraints**: Ensure your VM is `e2-micro`, standard persistent disk `30GB` or less, and in `us-central1`, `us-east1`, or `us-west1`.
3. **Keep the Server Running**: Unused static IPs cost a few cents a day. The IP is only free if the server is actively running!
