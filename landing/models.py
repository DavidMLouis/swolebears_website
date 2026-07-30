from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Marketing and Tracking
    source = models.CharField(max_length=255, blank=True, null=True)
    utm_source = models.CharField(max_length=255, blank=True, null=True)
    utm_medium = models.CharField(max_length=255, blank=True, null=True)
    utm_campaign = models.CharField(max_length=255, blank=True, null=True)
    utm_content = models.CharField(max_length=255, blank=True, null=True)
    utm_term = models.CharField(max_length=255, blank=True, null=True)
    landing_page = models.URLField(max_length=1024, blank=True, null=True)
    
    # Consent and Timestamps
    consent_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email


class QRCodeCampaign(models.Model):
    code_id = models.CharField(max_length=100, unique=True, db_index=True, help_text="Short identifier used in redirect URL (e.g., /s/launch-batch-1)")

    name = models.CharField(max_length=255, help_text="Human readable name for campaign")
    target_url = models.URLField(max_length=2048, help_text="Destination URL where scanners are redirected")
    description = models.TextField(blank=True, null=True)
    fg_color = models.CharField(max_length=7, default='#000000', help_text="Foreground color in hex (e.g. #000000)")
    bg_color = models.CharField(max_length=7, default='#FFFFFF', help_text="Background color in hex (e.g. #FFFFFF)")
    eye_color = models.CharField(max_length=20, default='', blank=True, help_text="Corner square / eye color in hex or name (e.g. #E52225 or swole-red)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code_id})"

    @property
    def total_scans(self):
        return self.scans.count()

    @property
    def human_scans(self):
        return self.scans.filter(is_bot=False).count()

    @property
    def bot_scans(self):
        return self.scans.filter(is_bot=True).count()

    @property
    def last_scanned(self):
        last_log = self.scans.order_by('-timestamp').first()
        return last_log.timestamp if last_log else None


class QRScanLog(models.Model):
    campaign = models.ForeignKey(QRCodeCampaign, on_delete=models.CASCADE, related_name='scans')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, default='Unknown')
    country = models.CharField(max_length=100, blank=True, default='Unknown')
    user_agent = models.TextField(blank=True, default='')
    device_type = models.CharField(max_length=50, default='Unknown') # e.g. Mobile (iOS), Mobile (Android), Desktop, Tablet
    browser = models.CharField(max_length=50, default='Unknown')
    os = models.CharField(max_length=50, default='Unknown')
    referrer = models.URLField(max_length=2048, blank=True, default='')
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Scan [{self.campaign.code_id}] at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - Bot: {self.is_bot}"

