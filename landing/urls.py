from django.urls import path
from .views import LandingPageView
from .qr_views import (
    DynamicQRRedirectView,
    QRAnalyticsDashboardView,
    QRCampaignAPIView,
    serve_qr_svg_preview,
    download_qr_code
)

app_name = 'landing'

urlpatterns = [
    path('', LandingPageView.as_view(), name='home'),
    path('s/<str:code_id>/', DynamicQRRedirectView.as_view(), name='qr_redirect'),
    path('r/<str:code_id>/', DynamicQRRedirectView.as_view(), name='qr_redirect_alt'),
    path('admin/qr-analytics/', QRAnalyticsDashboardView.as_view(), name='qr_analytics'),
    path('admin/qr-analytics/api/campaign/', QRCampaignAPIView.as_view(), name='qr_campaign_api'),
    path('admin/qr-analytics/preview/<str:code_id>/', serve_qr_svg_preview, name='qr_svg_preview'),
    path('admin/qr-analytics/download/<str:code_id>/<str:format_type>/', download_qr_code, name='qr_download'),
]


