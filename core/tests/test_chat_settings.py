"""Admin configuration and public rendering for the live-chat widget."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.test import TestCase

from core.chat_settings_views import ChatWidgetSuggestedButtonFormSet
from core.models import ChatWidgetSettings, ChatWidgetSuggestedButton, SiteSettings


class LiveChatSettingsTests(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.admin = User.objects.create_user(
            'chat-admin', 'chat-admin@example.com', 'pw-Strong-123!', is_staff=True,
        )
        self.admin.user_permissions.add(Permission.objects.get(codename='change_chatbotconversation'))
        self.client.force_login(self.admin)

    def valid_form_data(self, suggested_buttons=None, **overrides):
        data = {
            'enabled': 'on',
            'team_name': 'Support team',
            'suggested_buttons_heading': 'Choose a topic',
            'online_greeting': 'Hello, our team is online.',
            'offline_greeting': 'Leave a message for our team.',
            'contact_followup': 'We will reply {response_time}.',
            'whatsapp_number': '+91 98765 43210',
            'whatsapp_message': 'Hello from chat',
            'projects_url': '/catalog/',
            'privacy_url': 'https://projectshub.co.in/privacy/',
            'response_time': 'Within one business day',
        }
        data.update(overrides)
        settings = ChatWidgetSettings.get_settings()
        existing = list(settings.suggested_buttons.order_by('order', 'id'))
        rows = suggested_buttons if suggested_buttons is not None else [
            {
                'id': button.pk,
                'label': button.label,
                'prompt': button.prompt,
                'kind': button.kind,
                'order': button.order,
                'is_active': button.is_active,
            }
            for button in existing
        ]
        prefix = ChatWidgetSuggestedButtonFormSet.get_default_prefix()
        data[f'{prefix}-TOTAL_FORMS'] = str(len(rows))
        data[f'{prefix}-INITIAL_FORMS'] = str(len(existing))
        data[f'{prefix}-MIN_NUM_FORMS'] = '0'
        data[f'{prefix}-MAX_NUM_FORMS'] = '1000'
        for index, row in enumerate(rows):
            for field in ('id', 'label', 'kind', 'prompt', 'order'):
                if field in row:
                    data[f'{prefix}-{index}-{field}'] = str(row[field])
            data[f'{prefix}-{index}-is_active'] = 'on' if row.get('is_active', True) else ''
            data[f'{prefix}-{index}-DELETE'] = 'on' if row.get('delete', False) else ''
        return data

    def test_settings_page_saves_widget_urls_and_contact_details(self):
        response = self.client.post(
            '/admin/live-chat/settings/',
            self.valid_form_data(),
        )

        self.assertRedirects(response, '/admin/live-chat/settings/')
        settings = ChatWidgetSettings.get_settings()
        site_settings = SiteSettings.get_settings()
        self.assertEqual(settings.team_name, 'Support team')
        self.assertEqual(settings.suggested_buttons_heading, 'Choose a topic')
        self.assertEqual(settings.projects_url, '/catalog/')
        self.assertEqual(settings.privacy_url, 'https://projectshub.co.in/privacy/')
        self.assertEqual(site_settings.whatsapp_number, '+91 98765 43210')
        self.assertEqual(site_settings.response_time, 'Within one business day')

    def test_suggested_buttons_can_be_updated_added_and_hidden(self):
        existing = list(ChatWidgetSuggestedButton.objects.order_by('order'))
        rows = [
            {
                'id': button.pk,
                'label': button.label,
                'prompt': button.prompt,
                'kind': button.kind,
                'order': button.order,
                'is_active': button.is_active,
            }
            for button in existing
        ]
        rows[0].update(
            label='Find a project',
            prompt='Help me choose a project for my final year.',
            kind='question',
            order=1,
        )
        rows[1]['is_active'] = False
        rows[2]['delete'] = True
        rows.append({
            'label': 'Talk to support',
            'prompt': 'Please connect me to someone from the support team.',
            'kind': 'handoff',
            'order': len(existing) + 1,
            'is_active': True,
        })

        response = self.client.post(
            '/admin/live-chat/settings/',
            self.valid_form_data(suggested_buttons=rows),
        )

        self.assertRedirects(response, '/admin/live-chat/settings/')
        config = ChatWidgetSettings.get_settings().public_config()
        buttons_by_label = {button['label']: button for button in config['suggested_buttons']}
        self.assertEqual(
            buttons_by_label['Find a project'],
            {
                'label': 'Find a project',
                'prompt': 'Help me choose a project for my final year.',
                'kind': 'question',
            },
        )
        self.assertEqual(
            buttons_by_label['Talk to support'],
            {
                'label': 'Talk to support',
                'prompt': 'Please connect me to someone from the support team.',
                'kind': 'handoff',
            },
        )
        self.assertNotIn(existing[1].label, [button['label'] for button in config['suggested_buttons']])
        self.assertNotIn(existing[2].label, [button['label'] for button in config['suggested_buttons']])
        self.assertEqual(config['suggested_buttons_heading'], 'Choose a topic')
        public_page = self.client.get('/')
        self.assertContains(public_page, '"label": "Find a project"')
        self.assertContains(public_page, 'Help me choose a project for my final year.')
        self.assertContains(public_page, '"suggested_buttons_heading": "Choose a topic"')
        self.assertContains(public_page, '"kind": "handoff"')

    def test_suggested_buttons_are_not_limited_to_eight(self):
        existing = list(ChatWidgetSuggestedButton.objects.order_by('order'))
        rows = [
            {
                'id': button.pk,
                'label': button.label,
                'prompt': button.prompt,
                'kind': button.kind,
                'order': button.order,
                'is_active': True,
            }
            for button in existing
        ]
        rows.extend(
            {
                'label': f'Extra {index}',
                'prompt': f'Question {index}',
                'kind': 'question',
                'order': index + 5,
            }
            for index in range(10)
        )

        response = self.client.post(
            '/admin/live-chat/settings/',
            self.valid_form_data(suggested_buttons=rows),
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/admin/live-chat/settings/')
        self.assertEqual(ChatWidgetSuggestedButton.objects.count(), len(existing) + 10)

    def test_settings_page_shows_controls_for_suggested_buttons(self):
        response = self.client.get('/admin/live-chat/settings/')

        self.assertContains(response, 'Suggested buttons')
        self.assertContains(response, 'Add button')
        self.assertContains(response, 'Suggested buttons heading')
        self.assertContains(response, 'Button label')
        self.assertContains(response, 'Button action')
        self.assertContains(response, 'Question sent to chat')
        self.assertContains(response, 'Add as many buttons as you need')
        self.assertContains(response, 'name="suggested_buttons-__prefix__-settings"')
        self.assertContains(response, 'data-remove-suggested')

    def test_invalid_external_url_is_rejected_without_saving(self):
        response = self.client.post(
            '/admin/live-chat/settings/',
            self.valid_form_data(projects_url='javascript:alert(1)'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'External URLs must use HTTP or HTTPS')
        self.assertEqual(ChatWidgetSettings.get_settings().projects_url, '/projects/')

    def test_saved_values_are_exposed_to_the_public_widget(self):
        self.client.post(
            '/admin/live-chat/settings/',
            self.valid_form_data(projects_url='/custom-projects/'),
        )
        cache.clear()

        response = self.client.get('/')

        self.assertContains(response, 'ph-live-chat-config')
        self.assertContains(response, '"projects_url": "/custom-projects/"')
        self.assertContains(response, '"whatsapp_number": "919876543210"')

    def test_disabled_setting_is_reflected_in_public_widget_config(self):
        self.client.post(
            '/admin/live-chat/settings/',
            self.valid_form_data(enabled=''),
        )
        cache.clear()

        response = self.client.get('/')

        self.assertContains(response, '"enabled": false')

    def test_user_without_chat_permission_cannot_open_settings(self):
        self.client.logout()
        User = get_user_model()
        staff = User.objects.create_user('staff', 'staff@example.com', 'pw-Strong-123!', is_staff=True)
        self.client.force_login(staff)

        self.assertEqual(self.client.get('/admin/live-chat/settings/').status_code, 403)
