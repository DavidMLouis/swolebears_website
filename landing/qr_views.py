import json
import re
import urllib.request
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views import View
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from user_agents import parse

from .models import QRCodeCampaign, QRScanLog
from landing.management.commands.generate_qr import create_vector_svg_qr, DEFAULT_SVG_LOGO, DEFAULT_PNG_LOGO

# Known Bot / Crawler patterns
BOT_USER_AGENTS_REGEX = re.compile(
    r'(googlebot|bingbot|slurp|duckduckbot|baiduspider|yandexbot|sogou|exabot|facebot|facebookexternalhit|'
    r'twitterbot|linkedinbot|whatsapp|telegrambot|discordbot|slackbot|applebot|pinterest|bot|crawler|spider|'
    r'curl|wget|python-requests|aiohttp|httpx|postman|insomnia|headlesschrome|phantomjs)',
    re.IGNORECASE
)


def get_client_ip(request):
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_ip_location(ip):
    """
    Lookup city and country for an IP address.
    Handles private/local IPs gracefully and uses a quick 0.8s timeout for public IPs.
    """
    if not ip or ip in ['127.0.0.1', '::1', 'localhost'] or ip.startswith(('192.168.', '10.', '172.16.')):
        return 'Local Dev', 'Local Dev'

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city"
        req = urllib.request.Request(url, headers={'User-Agent': 'SwoleBearsQR/1.0'})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('status') == 'success':
                    city = data.get('city') or 'Unknown'
                    country = data.get('country') or 'Unknown'
                    return city, country
    except Exception:
        pass
    
    return 'Unknown', 'Unknown'


class DynamicQRRedirectView(View):
    """
    Endpoint: /s/<code_id>/
    Captures telemetry metadata before dynamically executing HTTP 302 redirect.
    """
    def get(self, request, code_id, *args, **kwargs):
        campaign = QRCodeCampaign.objects.filter(code_id=code_id, is_active=True).first()
        if not campaign:
            # If code not found or inactive, fallback to homepage or 404
            return redirect('landing:home')

        # 1. Capture Metadata
        ip_address = get_client_ip(request)
        user_agent_str = request.META.get('HTTP_USER_AGENT', '')
        referrer_str = request.META.get('HTTP_REFERER', '')

        # 2. Parse User-Agent & Device info
        user_agent_obj = parse(user_agent_str)
        is_bot = user_agent_obj.is_bot or bool(BOT_USER_AGENTS_REGEX.search(user_agent_str))

        if is_bot:
            device_type = 'Bot'
            os_name = 'Bot'
            browser_name = 'Bot'
        elif user_agent_obj.is_mobile:
            if 'iPhone' in user_agent_str or 'iOS' in user_agent_str:
                device_type = 'iOS Mobile'
            elif 'Android' in user_agent_str:
                device_type = 'Android Mobile'
            else:
                device_type = 'Mobile (Other)'
            os_name = user_agent_obj.os.family
            browser_name = user_agent_obj.browser.family
        elif user_agent_obj.is_tablet:
            device_type = 'Tablet'
            os_name = user_agent_obj.os.family
            browser_name = user_agent_obj.browser.family
        elif user_agent_obj.is_pc:
            device_type = 'Desktop'
            os_name = user_agent_obj.os.family
            browser_name = user_agent_obj.browser.family
        else:
            device_type = 'Other'
            os_name = user_agent_obj.os.family or 'Unknown'
            browser_name = user_agent_obj.browser.family or 'Unknown'

        # 3. Geolocation lookup
        city, country = get_ip_location(ip_address)

        # 4. Save Telemetry Log
        try:
            QRScanLog.objects.create(
                campaign=campaign,
                ip_address=ip_address,
                city=city,
                country=country,
                user_agent=user_agent_str[:500],
                device_type=device_type,
                browser=browser_name,
                os=os_name,
                referrer=referrer_str[:2048],
                is_bot=is_bot
            )
        except Exception as e:
            print(f"Error logging QR scan: {e}")

        # 5. Execute HTTP 302 Found Redirect to target URL
        return HttpResponseRedirect(campaign.target_url)


@method_decorator(staff_member_required, name='dispatch')
class QRAnalyticsDashboardView(View):
    """
    Internal View / Admin Panel: /admin/qr-analytics/
    Displays scan metrics, interactive charts, and live campaign target URL manager.
    """
    def get(self, request, *args, **kwargs):
        campaigns = QRCodeCampaign.objects.all()

        total_campaigns = campaigns.count()
        total_scans = QRScanLog.objects.count()
        human_scans = QRScanLog.objects.filter(is_bot=False).count()
        bot_scans = QRScanLog.objects.filter(is_bot=True).count()

        # Scans over time (last 30 days)
        last_30_days = timezone.now() - timedelta(days=30)
        daily_scans_qs = (
            QRScanLog.objects.filter(timestamp__gte=last_30_days)
            .annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(
                total=Count('id'),
                human=Count('id', filter=Q(is_bot=False)),
                bot=Count('id', filter=Q(is_bot=True))
            )
            .order_by('date')
        )

        dates_list = []
        human_counts = []
        bot_counts = []

        # Fill 30-day map
        daily_map = {item['date'].strftime('%Y-%m-%d'): item for item in daily_scans_qs if item['date']}
        for i in range(30):
            d = (timezone.now() - timedelta(days=29 - i)).strftime('%Y-%m-%d')
            dates_list.append(d)
            item = daily_map.get(d, {'human': 0, 'bot': 0})
            human_counts.append(item['human'])
            bot_counts.append(item['bot'])

        # Device distribution
        device_qs = (
            QRScanLog.objects.values('device_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        device_labels = [item['device_type'] for item in device_qs]
        device_data = [item['count'] for item in device_qs]

        # Geographic distribution (Countries)
        country_qs = (
            QRScanLog.objects.filter(is_bot=False)
            .values('country')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        country_labels = [item['country'] for item in country_qs]
        country_data = [item['count'] for item in country_qs]

        # Recent 30 scan logs
        recent_logs = QRScanLog.objects.select_related('campaign')[:30]

        context = {
            'campaigns': campaigns,
            'total_campaigns': total_campaigns,
            'total_scans': total_scans,
            'human_scans': human_scans,
            'bot_scans': bot_scans,
            'recent_logs': recent_logs,
            'dates_json': json.dumps(dates_list),
            'human_counts_json': json.dumps(human_counts),
            'bot_counts_json': json.dumps(bot_counts),
            'device_labels_json': json.dumps(device_labels),
            'device_data_json': json.dumps(device_data),
            'country_labels_json': json.dumps(country_labels),
            'country_data_json': json.dumps(country_data),
            'base_url': request.build_absolute_uri('/')[:-1]
        }

        return render(request, 'landing/qr_analytics.html', context)


@method_decorator(staff_member_required, name='dispatch')
class QRCampaignAPIView(View):
    """
    API view for creating/editing campaign destination URLs & retrieving live QR SVG previews.
    """
    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            code_id = data.get('code_id', '').strip()
            name = data.get('name', '').strip()
            target_url = data.get('target_url', '').strip()
            fg_color = data.get('fg_color', '#000000').strip()
            bg_color = data.get('bg_color', '#FFFFFF').strip()
            eye_color = data.get('eye_color', '').strip()
            is_active = data.get('is_active', True)

            if not code_id or not target_url:
                return JsonResponse({'success': False, 'error': 'Code ID and Target URL are required.'}, status=400)

            campaign, created = QRCodeCampaign.objects.get_or_create(
                code_id=code_id,
                defaults={
                    'name': name or f"Campaign {code_id}",
                    'target_url': target_url,
                    'fg_color': fg_color,
                    'bg_color': bg_color,
                    'eye_color': eye_color,
                    'is_active': is_active
                }
            )

            if not created:
                campaign.name = name if name else campaign.name
                campaign.target_url = target_url
                campaign.fg_color = fg_color
                campaign.bg_color = bg_color
                campaign.eye_color = eye_color
                campaign.is_active = is_active
                campaign.save()

            return JsonResponse({
                'success': True,
                'created': created,
                'code_id': campaign.code_id,
                'target_url': campaign.target_url,
                'message': f"Campaign '{campaign.code_id}' {'created' if created else 'updated'} successfully!"
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@staff_member_required
def serve_qr_svg_preview(request, code_id):
    """
    Serves a live SVG vector QR code preview for a campaign.
    """
    campaign = get_object_or_404(QRCodeCampaign, code_id=code_id)
    base_url = request.build_absolute_uri('/')[:-1]
    tracking_url = f"{base_url}/s/{campaign.code_id}"

    logo_path = str(DEFAULT_SVG_LOGO) if DEFAULT_SVG_LOGO.exists() else str(DEFAULT_PNG_LOGO)
    
    svg_data = create_vector_svg_qr(
        url=tracking_url,
        fg_color=campaign.fg_color,
        bg_color=campaign.bg_color,
        eye_color=campaign.eye_color,
        logo_path=logo_path,
        logo_ratio=0.22
    )

    return HttpResponse(svg_data, content_type='image/svg+xml')
