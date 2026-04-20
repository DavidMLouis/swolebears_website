from django.contrib import admin
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'created_at', 'utm_campaign')
    search_fields = ('email', 'first_name')
    list_filter = ('created_at', 'utm_source')
    readonly_fields = ('created_at',)
