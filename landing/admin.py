from django.contrib import admin
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'created_at', 'utm_campaign')
    search_fields = ('email', 'first_name')
    list_filter = ('created_at', 'utm_source')
    readonly_fields = ('created_at',)


from .models import QRCodeCampaign, QRScanLog

@admin.register(QRCodeCampaign)
class QRCodeCampaignAdmin(admin.ModelAdmin):
    list_display = ('code_id', 'name', 'target_url', 'is_active', 'total_scans', 'human_scans', 'created_at')
    search_fields = ('code_id', 'name', 'target_url', 'description')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QRScanLog)
class QRScanLogAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'timestamp', 'device_type', 'browser', 'os', 'ip_address', 'city', 'country', 'is_bot')
    search_fields = ('campaign__code_id', 'campaign__name', 'ip_address', 'user_agent', 'city', 'country')
    list_filter = ('is_bot', 'device_type', 'country', 'timestamp')
    readonly_fields = ('timestamp',)

