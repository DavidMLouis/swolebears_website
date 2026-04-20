import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

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
