from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from landing.models import QRCodeCampaign, QRScanLog
from services.qr_generator import create_vector_svg_qr



class QRCodePipelineTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign = QRCodeCampaign.objects.create(
            code_id='launch-batch-1',
            name='Launch Batch 1',
            target_url='https://swolebears.com/preorder',
            fg_color='#000000',
            bg_color='#FFFFFF'
        )
        self.staff_user = User.objects.create_user('admin', 'admin@example.com', 'password123', is_staff=True)


    def test_qr_campaign_creation_and_properties(self):
        """Test model fields and initial counters."""
        self.assertEqual(self.campaign.code_id, 'launch-batch-1')
        self.assertEqual(self.campaign.target_url, 'https://swolebears.com/preorder')
        self.assertEqual(self.campaign.total_scans, 0)
        self.assertEqual(self.campaign.human_scans, 0)
        self.assertEqual(self.campaign.bot_scans, 0)

    def test_dynamic_redirect_and_human_telemetry(self):
        """Test scanning /s/launch-batch-1 captures metadata and redirects."""
        response = self.client.get(
            reverse('landing:qr_redirect', kwargs={'code_id': 'launch-batch-1'}),
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            REMOTE_ADDR='127.0.0.1',
            HTTP_REFERER='https://instagram.com/'
        )

        # Check HTTP 302 redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://swolebears.com/preorder')

        # Check telemetry DB entry
        self.assertEqual(QRScanLog.objects.count(), 1)
        log = QRScanLog.objects.first()
        self.assertEqual(log.campaign, self.campaign)
        self.assertIn('iOS', log.device_type)
        self.assertFalse(log.is_bot)
        self.assertEqual(log.referrer, 'https://instagram.com/')
        self.assertEqual(self.campaign.total_scans, 1)
        self.assertEqual(self.campaign.human_scans, 1)

    def test_bot_crawler_filtering(self):
        """Test that crawler bots (Googlebot, WhatsApp, curl) are flagged as bots."""
        # 1. Googlebot scan
        self.client.get(
            reverse('landing:qr_redirect', kwargs={'code_id': 'launch-batch-1'}),
            HTTP_USER_AGENT='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        )

        # 2. Curl scan
        self.client.get(
            reverse('landing:qr_redirect', kwargs={'code_id': 'launch-batch-1'}),
            HTTP_USER_AGENT='curl/7.68.0'
        )

        self.assertEqual(QRScanLog.objects.count(), 2)
        bot_logs = QRScanLog.objects.filter(is_bot=True)
        self.assertEqual(bot_logs.count(), 2)
        self.assertEqual(self.campaign.human_scans, 0)
        self.assertEqual(self.campaign.bot_scans, 2)

    def test_dynamic_target_url_change(self):
        """Test changing destination URL in database updates redirect immediately."""
        # Update target URL in DB
        self.campaign.target_url = 'https://swolebears.com/new-promo'
        self.campaign.save()

        response = self.client.get(reverse('landing:qr_redirect', kwargs={'code_id': 'launch-batch-1'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://swolebears.com/new-promo')

    def test_analytics_dashboard_view_staff_access(self):
        """Test analytics dashboard requires staff login."""
        # Unauthenticated request should redirect to admin login
        response = self.client.get(reverse('landing:qr_analytics'))
        self.assertNotEqual(response.status_code, 200)

        # Staff user login
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('landing:qr_analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Swolé Bears')
        self.assertContains(response, 'launch-batch-1')

    def test_vector_svg_qr_generation(self):
        """Test programmatic SVG QR generation creates valid SVG string."""
        svg_output = create_vector_svg_qr(
            url='https://swolebears.com/s/launch-batch-1',
            fg_color='#111827',
            bg_color='#FFFFFF'
        )
        self.assertTrue(svg_output.startswith('<?xml') or '<svg' in svg_output)
        self.assertIn('xmlns', svg_output)

    def test_custom_corner_square_colors(self):
        """Test separate colors for baseline lines (#000000) and corner squares (Swole Red #E52225)."""
        svg_output = create_vector_svg_qr(
            url='https://swolebears.com/s/launch-batch-1',
            fg_color='#000000',
            bg_color='#FFFFFF',
            eye_color='swole-red'
        )
        self.assertIn('fill="#000000"', svg_output)
        self.assertIn('fill="#E52225"', svg_output)
        self.assertIn('id="qr-body-modules"', svg_output)
        self.assertIn('id="qr-corner-outer"', svg_output)
        self.assertIn('id="qr-corner-inner"', svg_output)
