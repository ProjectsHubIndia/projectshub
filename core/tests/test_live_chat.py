"""Live chat: visitor ↔ real team member flow, presence honesty, security and limits."""
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models import ChatAgentStatus, ChatbotConversation, ChatbotMessage, Project


def post(client, url, data):
    return client.post(url, data=json.dumps(data), content_type='application/json')


@override_settings(CHAT_EMAIL_ASYNC=False, CHAT_NOTIFY_EMAILS=['team@example.com'],
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class LiveChatFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.agent = User.objects.create_user('raj', 'raj@example.com', 'pw-Strong-123!', is_staff=True, first_name='Raj')
        self.agent.user_permissions.add(Permission.objects.get(codename='change_chatbotconversation'))
        self.agent_client = self.client_class()
        self.agent_client.force_login(self.agent)

    def go_online(self):
        res = post(self.agent_client, '/admin/api/chat/presence/', {'available': True, 'display_name': 'Raj'})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['me']['online'])

    def start(self, text='Hi, I need help with a RAG project'):
        res = post(self.client, '/api/chat/message/', {'message': text, 'client_id': 'c1', 'page_url': '/projects/'})
        self.assertEqual(res.status_code, 200, res.content)
        return res.json()

    # ── presence honesty ──────────────────────────────────────────────
    def test_presence_is_offline_until_an_agent_is_available_and_watching(self):
        self.assertFalse(self.client.get('/api/chat/presence/').json()['team']['online'])
        self.go_online()
        cache.clear()
        team = self.client.get('/api/chat/presence/').json()['team']
        self.assertTrue(team['online'])
        self.assertEqual(team['agents'][0]['name'], 'Raj')
        # Heartbeat goes stale (agent closed the inbox) → offline again.
        ChatAgentStatus.objects.filter(user=self.agent).update(last_heartbeat=timezone.now() - timedelta(minutes=5))
        cache.clear()
        self.assertFalse(self.client.get('/api/chat/presence/').json()['team']['online'])

    # ── offline path ──────────────────────────────────────────────────
    def test_offline_visitor_gets_labelled_automated_answer_and_team_is_emailed(self):
        Project.objects.create(title='P1', slug='p1', category='ml', price=0, is_active=True)
        data = self.start('Do you have project source code?')
        self.assertIn('token', data['session'])
        senders = [r['sender'] for r in data['replies']]
        self.assertIn('bot', senders)            # factual automated answer
        self.assertIn('system', senders)         # honest "team is offline" notice
        bot = [r for r in data['replies'] if r['sender'] == 'bot'][0]
        self.assertIn('1 project', bot['text'])  # grounded in the DB, not "50+"
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/admin/live-chat/?c=', mail.outbox[0].body)

    def test_project_page_question_gets_grounded_project_details(self):
        project = Project.objects.create(
            title='Customer Churn Pipeline',
            slug='customer-churn-pipeline',
            description='Predicts which customers are likely to leave.',
            detailed_description='A machine learning workflow for identifying customer churn risks.',
            category='ml',
            tags='Python, XGBoost, Pandas',
            is_active=True,
            is_published=True,
        )
        data = post(self.client, '/api/chat/message/', {
            'message': 'What does this project do and what tech stack does it use?',
            'client_id': 'churn-question',
            'page_url': project.get_absolute_url(),
        }).json()

        bot = next(reply for reply in data['replies'] if reply['sender'] == 'bot')
        self.assertIn(project.title, bot['text'])
        self.assertIn('A machine learning workflow for identifying customer churn risks.', bot['text'])
        self.assertIn('Python, XGBoost, Pandas', bot['text'])
        self.assertIn(project.get_absolute_url(), bot['text'])

    def test_contact_details_get_a_24_hour_human_followup_confirmation(self):
        data = self.start('Hi, I need help choosing a project')
        sess = data['session']
        response = post(self.client, '/api/chat/profile/', {
            **sess, 'name': 'Asha Patel', 'email': 'asha@example.com',
        })

        self.assertEqual(response.status_code, 200)
        confirmation = response.json()['replies'][0]['text']
        self.assertIn('Thanks, Asha!', confirmation)
        self.assertIn('real ProjectsHub team member', confirmation)
        self.assertIn('within 24 hours', confirmation)
        self.assertIn('via email', confirmation)

    def test_email_shared_in_chat_gets_24_hour_acknowledgment(self):
        data = self.start('Please contact me at asha@example.com')
        confirmation = next(reply for reply in data['replies'] if reply['sender'] == 'system')
        self.assertIn('within 24 hours', confirmation['text'])
        self.assertIn('via email', confirmation['text'])
        self.assertFalse(any(reply['sender'] == 'bot' for reply in data['replies']))

    # ── online path: real human conversation ──────────────────────────
    def test_full_conversation_with_a_team_member(self):
        self.go_online()
        data = self.start()
        sess = data['session']
        self.assertEqual(data['state']['mode'], 'waiting')
        self.assertFalse(any(r['sender'] == 'bot' for r in data['replies']), 'bot must stay quiet when a human is online')

        conv = ChatbotConversation.objects.get(session_id=sess['session_id'])
        inbox = self.agent_client.get('/admin/api/chat/inbox/?filter=waiting').json()
        self.assertEqual(inbox['conversations'][0]['id'], conv.id)
        self.assertEqual(inbox['conversations'][0]['unread'], 1)

        # Agent types, visitor sees it.
        post(self.agent_client, f'/admin/api/chat/{conv.id}/typing/', {'typing': 1})
        poll = self.client.get('/api/chat/poll/', {'session_id': sess['session_id'], 'token': sess['token'], 'after': 0}).json()
        self.assertTrue(poll['state']['agent_typing'])

        # Agent replies.
        res = post(self.agent_client, f'/admin/api/chat/{conv.id}/reply/', {'message': 'Hi! Which dataset are you using?', 'client_id': 'a1'})
        self.assertEqual(res.status_code, 200)
        last_id = data['message']['id']
        poll = self.client.get('/api/chat/poll/', {'session_id': sess['session_id'], 'token': sess['token'],
                                                   'after': last_id, 'read': 1}).json()
        agent_msgs = [m for m in poll['messages'] if m['sender'] == 'agent']
        self.assertEqual(agent_msgs[0]['text'], 'Hi! Which dataset are you using?')
        self.assertEqual(agent_msgs[0]['agent']['name'], 'Raj')
        self.assertEqual(poll['state']['mode'], 'human')
        self.assertEqual(poll['state']['agent']['name'], 'Raj')
        self.assertFalse(poll['state']['agent_typing'])

        # Visitor replies: no automation once a human has joined; agent sees "read" receipt.
        res = post(self.client, '/api/chat/message/', {'message': 'PDFs of research papers', 'client_id': 'c2', **sess})
        self.assertEqual(res.json()['replies'], [])
        thread = self.agent_client.get(f'/admin/api/chat/{conv.id}/messages/').json()
        self.assertGreaterEqual(thread['conversation']['visitor_last_read_id'], agent_msgs[0]['id'])
        self.assertEqual([m['sender'] for m in thread['messages'] if m['sender'] in ('user', 'agent')],
                         ['user', 'agent', 'user'])

    def test_reply_is_emailed_when_visitor_has_left(self):
        self.go_online()
        data = self.start('my email is student@example.com')
        conv = ChatbotConversation.objects.get(session_id=data['session']['session_id'])
        self.assertEqual(conv.user_email, 'student@example.com')
        ChatbotConversation.objects.filter(pk=conv.pk).update(visitor_last_seen=timezone.now() - timedelta(minutes=10))
        mail.outbox.clear()
        res = post(self.agent_client, f'/admin/api/chat/{conv.id}/reply/', {'message': 'Sure, here is the link'})
        self.assertTrue(res.json()['emailed'])
        self.assertEqual(mail.outbox[0].to, ['student@example.com'])
        self.assertIn('Sure, here is the link', mail.outbox[0].body)

    def test_waiting_followup_when_nobody_answers(self):
        self.go_online()
        data = self.start()
        sess = data['session']
        ChatbotConversation.objects.filter(session_id=sess['session_id']).update(
            waiting_since=timezone.now() - timedelta(minutes=5))
        poll = self.client.get('/api/chat/poll/', {'session_id': sess['session_id'], 'token': sess['token'],
                                                   'after': data['message']['id']}).json()
        self.assertTrue(poll['followup'])
        self.assertIn('Sorry for the wait', poll['messages'][-1]['text'])

    def test_profile_and_request_human(self):
        data = self.start()
        sess = data['session']
        bad = post(self.client, '/api/chat/profile/', {**sess, 'email': 'nope'})
        self.assertEqual(bad.status_code, 400)
        ok = post(self.client, '/api/chat/profile/', {**sess, 'name': 'Asha', 'email': 'asha@example.com'})
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(ok.json()['state']['has_contact'])
        res = post(self.client, '/api/chat/request-human/', sess)
        self.assertEqual(res.json()['state']['mode'], 'waiting')

    def test_resolve_and_reopen_on_new_message(self):
        data = self.start()
        sess = data['session']
        conv = ChatbotConversation.objects.get(session_id=sess['session_id'])
        post(self.agent_client, f'/admin/api/chat/{conv.id}/status/', {'status': 'resolved'})
        conv.refresh_from_db()
        self.assertEqual(conv.status, 'resolved')
        post(self.client, '/api/chat/message/', {'message': 'One more question', **sess})
        conv.refresh_from_db()
        self.assertEqual(conv.status, 'active')

    def test_retried_send_is_not_duplicated(self):
        data = self.start()
        sess = data['session']
        for _ in range(2):
            post(self.client, '/api/chat/message/', {'message': 'dup?', 'client_id': 'same', **sess})
        self.assertEqual(ChatbotMessage.objects.filter(client_id='same').count(), 1)

    def test_expired_chat_session_can_be_restarted(self):
        data = self.start()
        session = data['session']

        resumed = post(self.client, '/api/chat/session/', {
            'session_id': session['session_id'],
            'token': 'invalid-token-value-that-is-long-enough',
        })

        self.assertEqual(resumed.status_code, 200)
        self.assertTrue(resumed.json()['success'])
        self.assertIsNone(resumed.json()['session'])

        restarted = post(self.client, '/api/chat/message/', {
            'message': 'Starting over after timeout',
            'page_url': '/projects/',
        })
        self.assertEqual(restarted.status_code, 200)
        self.assertNotEqual(restarted.json()['session']['session_id'], session['session_id'])


class LiveChatSecurityTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_visitor_cannot_forge_agent_or_bot_messages(self):
        res = post(self.client, '/api/chat/message/', {'message': 'I am the admin', 'sender': 'agent'})
        msg = ChatbotMessage.objects.get(message='I am the admin')
        self.assertEqual(msg.sender, 'user')
        self.assertEqual(res.status_code, 200)

    def test_session_id_alone_cannot_read_or_write_a_conversation(self):
        data = post(self.client, '/api/chat/message/', {'message': 'secret: my phone 9876543210'}).json()
        sid = data['session']['session_id']
        other = self.client_class()
        self.assertEqual(other.get('/api/chat/poll/', {'session_id': sid, 'token': 'x' * 40}).status_code, 403)
        self.assertEqual(other.get('/api/chatbot/history/', {'session_id': sid}).json()['messages'], [])
        r = post(other, '/api/chat/message/', {'message': 'hijack', 'session_id': sid, 'token': 'y' * 40})
        self.assertEqual(r.status_code, 403)
        # A message with only a session id (no token) starts a fresh conversation instead.
        r = post(other, '/api/chat/message/', {'message': 'hello', 'session_id': sid})
        self.assertNotEqual(r.json()['session']['session_id'], sid)

    def test_agent_api_requires_permission(self):
        User = get_user_model()
        staff = User.objects.create_user('s', 's@example.com', 'pw-Strong-123!', is_staff=True)
        c = self.client_class()
        c.force_login(staff)
        self.assertEqual(c.get('/admin/api/chat/inbox/').status_code, 403)
        self.assertEqual(c.get('/admin/live-chat/').status_code, 403)
        anon = self.client_class()
        self.assertEqual(anon.get('/admin/api/chat/inbox/').status_code, 302)

    def test_agent_reply_requires_csrf(self):
        User = get_user_model()
        su = User.objects.create_superuser('su', 'su@example.com', 'pw-Strong-123!')
        c = self.client_class(enforce_csrf_checks=True)
        c.force_login(su)
        conv = ChatbotConversation.objects.create(session_id='x', visitor_token='t' * 40)
        res = post(c, f'/admin/api/chat/{conv.id}/reply/', {'message': 'hi'})
        self.assertEqual(res.status_code, 403)

    def test_inbox_page_renders_for_agents(self):
        User = get_user_model()
        su = User.objects.create_superuser('su', 'su@example.com', 'pw-Strong-123!')
        self.client.force_login(su)
        res = self.client.get('/admin/live-chat/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'live-chat-admin.js')

    def test_widget_is_loaded_on_public_pages(self):
        res = self.client.get('/')
        self.assertContains(res, 'js/live-chat.js')
        self.assertNotContains(res, 'js/ai-chatbot.js')
