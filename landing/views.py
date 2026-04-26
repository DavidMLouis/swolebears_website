import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from django.conf import settings

from .forms import SubscriberForm
from .models import Subscriber
from services.google_sheets import GoogleSheetsService

class LandingPageView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        form = SubscriberForm()
        return render(request, 'landing/home.html', {'form': form})

    def post(self, request, *args, **kwargs):
        # Determine if request is JSON (Fetch API) or standard urlencoded
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        else:
            data = request.POST

        form = SubscriberForm(data)

        if form.is_valid():
            try:
                # 1. Save to Django DB
                subscriber = form.save(commit=False)
                
                # Capture optional marketing params
                subscriber.source = data.get('source', '')
                subscriber.utm_source = data.get('utm_source', '')
                subscriber.utm_medium = data.get('utm_medium', '')
                subscriber.utm_campaign = data.get('utm_campaign', '')
                subscriber.utm_content = data.get('utm_content', '')
                subscriber.utm_term = data.get('utm_term', '')
                subscriber.landing_page = data.get('landing_page', request.build_absolute_uri())
                
                # Check for existing email to prevent integrity errors but treat as success
                if Subscriber.objects.filter(email=subscriber.email).exists():
                    return JsonResponse({'success': True, 'message': 'You are already on the waitlist!'})

                subscriber.save()

                # 2. Sync to Google Sheets
                sheets_service = GoogleSheetsService()
                subscriber_dict = {
                    'email': subscriber.email,
                    'first_name': subscriber.first_name,
                    'source': subscriber.source,
                    'utm_source': subscriber.utm_source,
                    'utm_medium': subscriber.utm_medium,
                    'utm_campaign': subscriber.utm_campaign,
                    'utm_content': subscriber.utm_content,
                    'utm_term': subscriber.utm_term,
                    'landing_page': subscriber.landing_page,
                    'consent_status': subscriber.consent_status,
                }
                sheets_service.append_subscriber(subscriber_dict)

                # 3. Send automatic welcome email
                email_subject = "Welcome to Swolé Bears!"
                email_body = """Hey,

Really appreciate you checking out Swolé Bears.

We’re building something a little different — a clean, no-shaker way to hit your protein without dealing with powders or shakes.
I want to learn more about you a bit more, so I can make it as good as possible.

Quick question for you:

What do you currently do for protein or staying healthy? Anything you’re into?
Would love to hear about it.

Cheers,

--
David M. Louis | Founder
Swolé Bears - Pre-order Now swolebears.com"""

                html_message = """\
<p style="font-family: Arial, sans-serif; font-size: 15px; color: #222;">Hey,</p>
<p style="font-family: Arial, sans-serif; font-size: 15px; color: #222;">Really appreciate you checking out Swolé Bears.</p>
<p style="font-family: Arial, sans-serif; font-size: 15px; color: #222;">We’re building something a little different — a clean, no-shaker way to hit your protein without dealing with powders or shakes.<br>
I want to learn more about you a bit more, so I can make it as good as possible.</p>
<p style="font-family: Arial, sans-serif; font-size: 15px; color: #222;">Quick question for you:</p>
<p style="font-family: Arial, sans-serif; font-size: 15px; color: #222;">What do you currently do for protein or staying healthy? Anything you’re into?<br>
Would love to hear about it.</p>
<p style="font-family: Arial, sans-serif; font-size: 15px; color: #222;">Cheers,</p>

<p style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.5; margin-top: 20px;">
    -----------------------------<br>
    David M. Louis | <em>Founder</em><br>
    <strong>Swolé Bears - Pre-order Now</strong> <a href="https://swolebears.com" style="color: blue; text-decoration: none;">swolebears.com</a><br>
    <br>
    <a href="https://instagram.com/swolebearsgummy"><img src="https://img.icons8.com/fluency/48/instagram-new.png" width="24" height="24" alt="Instagram" style="margin-right: 5px;"></a>
    <a href="https://tiktok.com/@swolebears"><img src="https://img.icons8.com/ios-filled/50/tiktok.png" width="24" height="24" alt="TikTok" style="margin-right: 5px;"></a>
    <a href="https://youtube.com/@swolebears"><img src="https://img.icons8.com/color/48/youtube-play.png" width="24" height="24" alt="YouTube" style="margin-right: 5px;"></a>
    <a href="https://www.facebook.com/groups/swolebearslaunch"><img src="https://img.icons8.com/color/48/facebook-new.png" width="24" height="24" alt="Facebook"></a>
</p>
"""
                try:
                    send_mail(
                        subject=email_subject,
                        message=email_body, # Fallback for plain text clients
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        fail_silently=True,
                        html_message=html_message # Sends the rich HTML email
                    )
                except Exception as email_err:
                    print(f"Failed to send email to {subscriber.email}: {email_err}")

                return JsonResponse({'success': True, 'message': 'Successfully joined the waitlist!'})

            except Exception as e:
                return JsonResponse({'success': False, 'error': 'An internal error occurred. Please try again.'}, status=500)
        else:
            # Form is invalid
            # Check if it was because of honeypot
            if 'honeypot' in form.errors:
                 # Silently fail for bots
                 return JsonResponse({'success': True, 'message': 'Successfully joined the waitlist!'})
                 
            # Extract first error message
            error_message = 'Please check your information and try again.'
            for field, errors in form.errors.items():
                if errors:
                    error_message = errors[0]
                    break
                    
            return JsonResponse({'success': False, 'error': error_message}, status=400)
