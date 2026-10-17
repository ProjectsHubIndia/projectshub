from urllib.parse import urlsplit

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import redirect, render

from .models import ChatWidgetSettings, ChatWidgetSuggestedButton, SiteSettings


def validate_chat_url(value):
    value = value.strip()
    if not value or '\\' in value or any(char in value for char in '\r\n\t'):
        raise ValidationError('Enter an HTTPS/HTTP URL or a site-relative path beginning with /.')
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ValidationError('Enter a valid URL or site-relative path.') from exc

    if parsed.scheme:
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            raise ValidationError('External URLs must use HTTP or HTTPS and include a host.')
        URLValidator(schemes=['http', 'https'])(value)
    elif not value.startswith('/') or value.startswith('//') or parsed.netloc:
        raise ValidationError('Use a site-relative path beginning with / or a complete HTTP(S) URL.')


class LiveChatSettingsForm(forms.Form):
    enabled = forms.BooleanField(required=False, label='Enable the live chat widget')
    team_name = forms.CharField(max_length=80, label='Name shown to visitors')
    suggested_buttons_heading = forms.CharField(
        max_length=60, required=False, label='Suggested buttons heading',
    )
    online_greeting = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Greeting when an agent is online',
    )
    offline_greeting = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Greeting when the team is away',
    )
    contact_followup = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Contact follow-up message',
    )
    whatsapp_number = forms.CharField(max_length=50, label='WhatsApp number')
    whatsapp_message = forms.CharField(max_length=200, label='WhatsApp pre-filled message')
    projects_url = forms.CharField(
        max_length=500, validators=[validate_chat_url],
        label='Projects link',
    )
    privacy_url = forms.CharField(
        max_length=500, validators=[validate_chat_url],
        label='Privacy link',
    )
    response_time = forms.CharField(max_length=100, label='Offline response-time estimate')

    def clean_team_name(self):
        value = self.cleaned_data['team_name'].strip()
        if not value:
            raise ValidationError('Enter the name visitors should see.')
        return value

    def clean_whatsapp_number(self):
        value = self.cleaned_data['whatsapp_number'].strip()
        digits = ''.join(char for char in value if char.isdigit())
        if not 7 <= len(digits) <= 20:
            raise ValidationError('Enter a WhatsApp number with 7 to 20 digits, including country code.')
        return value

    def clean_response_time(self):
        value = self.cleaned_data['response_time'].strip()
        if not value:
            raise ValidationError('Enter the expected response time shown to visitors.')
        return value


ChatWidgetSuggestedButtonFormSet = inlineformset_factory(
    ChatWidgetSettings,
    ChatWidgetSuggestedButton,
    fields=('label', 'kind', 'prompt', 'order', 'is_active'),
    extra=0,
    can_delete=True,
    widgets={
        'label': forms.TextInput(attrs={'placeholder': 'e.g. Browse AI projects'}),
        'prompt': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Question sent when a visitor clicks this button'}),
        'order': forms.NumberInput(attrs={'min': 0}),
    },
)


@staff_member_required(login_url='admin:login')
def admin_live_chat_settings_view(request):
    if not request.user.has_perm('core.change_chatbotconversation'):
        raise PermissionDenied

    chat_settings = ChatWidgetSettings.get_settings()
    site_settings = SiteSettings.get_settings()
    initial = {
        'enabled': chat_settings.enabled,
        'team_name': chat_settings.team_name,
        'suggested_buttons_heading': chat_settings.suggested_buttons_heading,
        'online_greeting': chat_settings.online_greeting,
        'offline_greeting': chat_settings.offline_greeting,
        'contact_followup': chat_settings.contact_followup,
        'whatsapp_number': site_settings.whatsapp_number,
        'whatsapp_message': chat_settings.whatsapp_message,
        'projects_url': chat_settings.projects_url,
        'privacy_url': chat_settings.privacy_url,
        'response_time': site_settings.response_time,
    }

    if request.method == 'POST':
        form = LiveChatSettingsForm(request.POST)
        button_formset = ChatWidgetSuggestedButtonFormSet(request.POST, instance=chat_settings)
        if form.is_valid() and button_formset.is_valid():
            values = form.cleaned_data
            with transaction.atomic():
                for field in (
                    'enabled', 'team_name', 'suggested_buttons_heading', 'online_greeting', 'offline_greeting',
                    'contact_followup', 'whatsapp_message', 'projects_url', 'privacy_url',
                ):
                    setattr(chat_settings, field, values[field])
                chat_settings.save()
                button_formset.save()
                site_settings.whatsapp_number = values['whatsapp_number']
                site_settings.response_time = values['response_time']
                site_settings.save(update_fields=['whatsapp_number', 'response_time'])
                cache.delete('site_context_settings')
            messages.success(request, 'Live Chat settings saved.')
            return redirect('admin_live_chat_settings')
    else:
        form = LiveChatSettingsForm(initial=initial)
        button_formset = ChatWidgetSuggestedButtonFormSet(instance=chat_settings)

    return render(request, 'admin/live_chat_settings.html', {
        'title': 'Live Chat Settings',
        'form': form,
        'button_formset': button_formset,
    })
