from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    # Hidden honeypot field to catch spam bots
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="Leave empty"
    )

    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'consent_status']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 text-white placeholder-gray-400',
                'placeholder': 'Enter your email',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 text-white placeholder-gray-400',
                'placeholder': 'First name (optional)'
            }),
            'consent_status': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 rounded bg-gray-800 border-gray-600 focus:ring-red-500 text-red-600',
                'required': True
            })
        }

    def clean_honeypot(self):
        """Check that nothing has been entered into the honeypot."""
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            # If honeypot has data, it's likely a bot.
            raise forms.ValidationError('Spam detected.')
        return honeypot
