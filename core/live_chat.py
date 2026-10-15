"""
core/live_chat.py — Live (human) chat service layer for the website chat widget.

Principles
- Visitors talk to real ProjectsHub team members, who reply from /admin/live-chat/.
- Team presence is real: an agent counts as online only while they are set to Available
  AND their Live Chat inbox is open (heartbeat within ChatAgentStatus.ONLINE_WINDOW_SECONDS).
- The automated assistant only answers while nobody is available, is always labelled as
  automated, and only states facts read from the database (no invented numbers or SLAs).
- Works on shared hosting: short polling, no websockets, no background workers; state that
  must be shared across worker processes (typing, presence) lives in the database.
"""
import logging
import re
import secrets
import threading
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils import timezone

from .models import (
    AITool, BlogPost, ChatAgentStatus, ChatbotConversation, ChatbotMessage, FAQ, PricingPlan, Project,
    Service, SiteSettings, WorkshopCard,
)

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 1000
VISITOR_ONLINE_SECONDS = 45
TYPING_SECONDS = 6
WAITING_FOLLOWUP_SECONDS = 180
VISITOR_EMAIL_COOLDOWN = timedelta(minutes=10)
AVATAR_COLORS = ['#4f46e5', '#0891b2', '#7c3aed', '#059669', '#db2777', '#d97706', '#2563eb']


# ── Identity helpers ──────────────────────────────────────────────────────────

def new_session_credentials():
    return 'chat_' + secrets.token_hex(12), secrets.token_urlsafe(32)


def get_conversation(session_id, token):
    """Return the conversation only if the visitor presents the matching secret token."""
    session_id = (session_id or '').strip()
    token = (token or '').strip()
    if not session_id or not token or len(token) < 20:
        return None
    conv = ChatbotConversation.objects.filter(session_id=session_id).first()
    if conv and conv.visitor_token and secrets.compare_digest(conv.visitor_token, token):
        return conv
    return None


def initials(name):
    parts = [p for p in (name or '').replace('.', ' ').split() if p]
    if not parts:
        return 'PH'
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else '')).upper()


def avatar_color(seed):
    return AVATAR_COLORS[sum(ord(c) for c in str(seed)) % len(AVATAR_COLORS)]


def agent_public(user):
    if not user:
        return None
    status = getattr(user, 'chat_status', None)  # reverse one-to-one; None when not set up
    name = status.public_name if status else (user.first_name or user.get_username())
    online = bool(status and status.is_online)
    return {'id': user.pk, 'name': name, 'initials': initials(name), 'color': avatar_color(user.pk), 'online': online}


# ── Presence ──────────────────────────────────────────────────────────────────

def online_agents():
    cutoff = timezone.now() - timedelta(seconds=ChatAgentStatus.ONLINE_WINDOW_SECONDS)
    return list(
        ChatAgentStatus.objects.select_related('user')
        .filter(is_available=True, last_heartbeat__gte=cutoff, user__is_active=True, user__is_staff=True)
        .order_by('-last_heartbeat')
    )


def team_presence():
    agents = online_agents()
    try:
        response_time = SiteSettings.get_settings().response_time
    except Exception:
        response_time = 'Within 24 hours'
    return {
        'online': bool(agents),
        'agents': [
            {'name': a.public_name, 'initials': initials(a.public_name), 'color': avatar_color(a.user_id)}
            for a in agents[:3]
        ],
        'offline_response_time': response_time,
    }


# ── Serialisation ─────────────────────────────────────────────────────────────

def serialize_message(msg):
    data = {
        'id': msg.id,
        'sender': msg.sender,
        'text': msg.message,
        'timestamp': msg.timestamp.isoformat(),
        'client_id': msg.client_id or None,
    }
    if msg.sender == 'agent':
        data['agent'] = agent_public(msg.agent) or {'name': 'ProjectsHub team', 'initials': 'PH', 'color': AVATAR_COLORS[0]}
    return data


def conversation_state(conv, now=None):
    now = now or timezone.now()
    return {
        'mode': conv.mode,
        'status': conv.status,
        'agent': agent_public(conv.assigned_agent),
        'agent_typing': bool(conv.agent_typing_until and conv.agent_typing_until > now),
        'agent_typing_name': (cache.get(f'chat_typing_agent:{conv.pk}') or '') if (conv.agent_typing_until and conv.agent_typing_until > now) else '',
        'followup_prompted': conv.followup_prompted,
        'last_read_by_team': conv.agent_last_read_id,
        'visitor': {'name': conv.user_name, 'email': conv.user_email, 'phone': conv.user_phone},
        'has_contact': bool(conv.user_email or conv.user_phone),
    }


# ── Message creation ──────────────────────────────────────────────────────────

def add_message(conv, sender, text, agent=None, client_id=''):
    msg = ChatbotMessage.objects.create(
        conversation=conv, sender=sender, message=text, agent=agent, client_id=client_id or '',
    )
    ChatbotConversation.objects.filter(pk=conv.pk).update(last_message_at=msg.timestamp, updated_at=msg.timestamp)
    conv.last_message_at = msg.timestamp
    return msg


def _site_facts():
    facts = {'projects': 0, 'tools': 0, 'workshop': None, 'response_time': 'Within 24 hours'}
    try:
        facts['projects'] = Project.objects.filter(is_active=True, is_published=True).count()
        facts['tools'] = AITool.objects.filter(is_published=True).count()
        w = (WorkshopCard.objects.filter(is_active=True).order_by('-is_featured', 'order', '-created_at').first())
        if w:
            facts['workshop'] = w
        facts['response_time'] = SiteSettings.get_settings().response_time or facts['response_time']
    except Exception:
        logger.exception('live_chat: failed to load site facts')
    return facts


def _project_for_question(text, page_url=''):
    """Find a published project from the page being viewed or an explicit title mention."""
    try:
        path_parts = [part for part in urlsplit(page_url or '').path.split('/') if part]
    except ValueError:
        path_parts = []
    current_project = None
    if len(path_parts) >= 2 and path_parts[0] == 'projects':
        project_query = {'pk': path_parts[1]} if path_parts[1].isdigit() else {'slug': path_parts[1]}
        current_project = (
            Project.objects.filter(is_active=True, is_published=True, **project_query)
            .prefetch_related('technologies')
            .first()
        )

    msg = (text or '').lower()
    if current_project and any(phrase in msg for phrase in (
        'this project', 'this one', 'tell me about this', 'what is this',
        'what does it', 'how does it', 'what technology', 'which technology',
        'tech stack', 'features', 'overview', 'details', 'how much', 'price', 'pricing', 'cost',
    )):
        return current_project

    ignored = {
        'about', 'does', 'have', 'with', 'from', 'your', 'tell', 'show',
        'what', 'which', 'where', 'when', 'this', 'that', 'project', 'projects',
        'details', 'overview', 'technology', 'technologies', 'stack', 'feature',
        'features', 'work', 'works', 'available', 'looking', 'need', 'want',
    }
    terms = {word for word in re.findall(r'[a-z0-9]+', msg) if len(word) > 2 and word not in ignored}
    if not terms:
        return None

    match = Q()
    for term in terms:
        match |= (
            Q(title__icontains=term) | Q(slug__icontains=term) |
            Q(tags__icontains=term) | Q(description__icontains=term) |
            Q(detailed_description__icontains=term) |
            Q(technologies__name__icontains=term)
        )

    candidates = (
        Project.objects.filter(is_active=True, is_published=True)
        .filter(match)
        .distinct()
        .prefetch_related('technologies')
        .order_by('order', 'title')[:20]
    )
    best_project = None
    best_score = 0
    for project in candidates:
        title_terms = set(re.findall(r'[a-z0-9]+', f'{project.title} {project.slug}'.lower()))
        title_matches = len(title_terms & terms)
        if title_matches:
            score = title_matches * 4
            score += sum(term in (project.tags or '').lower() for term in terms)
            score += sum(term in project.description.lower() for term in terms)
            if score > best_score:
                best_project, best_score = project, score
    return best_project


def _project_answer(project):
    description = strip_tags(project.subtitle or project.detailed_description or project.description)
    description = ' '.join(description.split())
    if len(description) > 320:
        description = description[:317].rsplit(' ', 1)[0] + '...'

    parts = [f"Sure! {project.title}:"]
    if description:
        parts.append(description)
    technologies = project.get_tags_list()[:5]
    if technologies:
        parts.append('It uses ' + ', '.join(technologies) + '.')
    if project.price_label or project.price:
        parts.append(f"Listed price: {project.price_label or project.price}.")
    parts.append(f"Take a look: {project.get_absolute_url()}")
    parts.append('What would you like to know about it?')
    return ' '.join(parts)


def contact_confirmation(conv):
    """Confirm saved contact details and set the team's stated follow-up expectation."""
    channels = []
    if conv.user_email:
        channels.append('email')
    if conv.user_phone:
        channels.append('phone/WhatsApp')
    contact_route = ' and '.join(channels) or 'your preferred contact method'
    greeting = f", {conv.user_name.split()[0]}" if conv.user_name else ''
    return (
        f"Thanks{greeting}! We've got your details. A real ProjectsHub team member will reach out "
        f"within 24 hours via {contact_route}. You can keep chatting with us here too."
    )


def automated_answer(text, page_url='', contact_captured=False):
    """Give conversational answers using published projects and live database facts."""
    msg = (text or '').lower()
    f = _site_facts()

    def has(*words):
        return any(w in msg for w in words)

    faq = _faq_for_question(text)
    if faq:
        answer = strip_tags(faq.answer or '').strip()
        if answer:
            return f"{answer} More details: {faq.get_absolute_url()}"

    if has('workshop', 'bootcamp', 'course', 'training', 'class'):
        w = f['workshop']
        if w:
            parts = [f"Our current workshop is \"{w.title}\""]
            if w.date:
                parts.append(f"({w.date}{', ' + w.time if w.time else ''}, {w.mode})")
            price = w.price_label or ('Free' if not w.price else w.price)
            parts.append(f"Price: {price}.")
            return ' '.join(parts) + f". Full details and the day-by-day plan: /workshop/{w.pk}/"
        return "Workshop details are listed at /workshop/ — a team member can tell you about upcoming batches."
    if has('price', 'pricing', 'cost', 'fee', 'quote', 'budget', 'charges'):
        project = _project_for_question(text, page_url)
        if project:
            return _project_answer(project)
        plans = list(PricingPlan.objects.filter(is_active=True).prefetch_related('features').order_by('order')[:10])
        if plans:
            details = []
            for plan in plans:
                if plan.is_free:
                    price = 'Free'
                else:
                    price = f"monthly {plan.monthly_price}, yearly {plan.yearly_price}"
                details.append(f"{plan.name}: {price}")
            return (
                "Current listed pricing: " + '; '.join(details) +
                ". The site does not specify a currency here. Project prices appear on their individual pages; "
                "custom work is quoted after the team understands your requirements."
            )
        return ("Pricing depends on the project or service. Each project page lists its price, and for custom "
                "work the team will give you a quote once they understand what you need.")
    service = _service_for_question(text)
    if service:
        description = strip_tags(service.short_description or service.full_description or '').strip()
        answer = f"{service.title}: {description}" if description else service.title
        return f"{answer} Details: {service.get_absolute_url()}"
    if has('blog', 'article', 'tutorial', 'post'):
        article = _blog_for_question(text)
        if article:
            summary = strip_tags(article.get_lead() or '').strip()
            answer = f"{article.title}: {summary}" if summary else article.title
            return f"{answer} Read: {article.get_absolute_url()}"
        return "Browse published articles and tutorials at /blog/."
    if has('custom', 'hire', 'business', 'company', 'mvp', 'develop', 'build', 'automation', 'integration'):
        services = list(Service.objects.filter(is_published=True).order_by('sort_order', 'title')[:10])
        if services:
            offerings = '; '.join(
                f"{item.title}: {strip_tags(item.short_description or item.full_description or '').strip()}"
                for item in services
            )
            return f"Our services include {offerings} Details: /services/ . Tell us what you want to build and the team can follow up."
        return ("We build custom AI solutions — development, automation and API integration. Overview: "
                "/services/ai-development/ . Tell us a bit about what you want to build and a team member will follow up.")
    project = _project_for_question(text, page_url)
    if project:
        return _project_answer(project)
    if has('project', 'source code', 'code', 'github', 'final year', 'capstone', 'repo'):
        n = f['projects']
        count = f"{n} project{'s' if n != 1 else ''}" if n else 'projects'
        return f"You can browse {count} with source code and documentation at /projects/ . Tell us your topic or stack and we'll suggest a fit."
    if has('tool', 'free'):
        n = f['tools']
        return f"Our free tools directory{' (' + str(n) + ' tools)' if n else ''} is at /tools/ ."
    if has('contact', 'call', 'phone', 'whatsapp', 'email') and not contact_captured:
        return "You can reach the team on WhatsApp using the button at the top of this chat, or via /contact/ ."
    return ''


def _question_terms(text):
    ignored = {
        'about', 'after', 'also', 'and', 'are', 'article', 'blog', 'can', 'could', 'does', 'for', 'from', 'have',
        'help', 'how', 'into', 'please', 'project', 'projects', 'tell', 'that', 'the', 'their',
        'there', 'this', 'what', 'when', 'where', 'which', 'who', 'with', 'would', 'your',
        'post', 'tutorial',
        'bootcamp', 'class', 'code', 'contact', 'cost', 'course', 'fee', 'free', 'price',
        'pricing', 'service', 'services', 'source', 'tool', 'tools', 'training', 'workshop',
    }
    terms = set()
    for term in re.findall(r'[a-z0-9]+', (text or '').lower()):
        if len(term) > 2 and term not in ignored:
            if len(term) > 5 and term.endswith('ies'):
                term = term[:-3] + 'y'
            elif len(term) > 4 and term.endswith('s'):
                term = term[:-1]
            terms.add(term)
    return terms


def _best_text_match(text, records, fields):
    terms = _question_terms(text)
    if not terms:
        return None

    best_record = None
    best_score = 0
    best_matches = set()
    for record in records:
        record_terms = set()
        for field in fields:
            record_terms.update(_question_terms(getattr(record, field, '')))
        matches = terms & record_terms
        score = len(matches)
        if score > best_score:
            best_record, best_score, best_matches = record, score, matches

    if best_score >= 2 or any(len(term) >= 6 for term in best_matches):
        return best_record
    return None


def _faq_for_question(text):
    faqs = FAQ.objects.filter(is_published=True).order_by('sort_order', 'id')
    return _best_text_match(text, faqs, ('question',))


def _service_for_question(text):
    services = Service.objects.filter(is_published=True).order_by('sort_order', 'title')[:30]
    return _best_text_match(text, services, ('title', 'short_description', 'full_description'))


def _blog_for_question(text):
    posts = BlogPost.objects.filter(is_active=True, is_published=True).order_by('order', '-published_at')[:50]
    return _best_text_match(text, posts, ('title', 'lead', 'excerpt'))


def handle_visitor_message(conv, text, first_user_message=False, contact_captured=False):
    """
    Decide what (if anything) is sent back immediately after a visitor message.
    Returns a list of ChatbotMessage objects created by the system/bot.
    """
    replies = []
    now = timezone.now()

    if conv.status in ('resolved', 'archived'):
        conv.status = 'active'
        conv.save(update_fields=['status'])

    if conv.mode == 'human':
        # A team member is already handling this chat — never interrupt with automation.
        notify_team(conv, reason='message')
        return replies

    agents = online_agents()
    if agents:
        if conv.mode != 'waiting':
            conv.mode = 'waiting'
            conv.waiting_since = now
            conv.followup_prompted = False
            conv.save(update_fields=['mode', 'waiting_since', 'followup_prompted'])
            names = ', '.join(a.public_name for a in agents[:2])
            replies.append(add_message(
                conv, 'system',
                f"You're connected to the ProjectsHub team. {names} {'is' if len(agents) == 1 else 'are'} online and will reply here shortly.",
            ))
        if contact_captured:
            replies.append(add_message(conv, 'system', contact_confirmation(conv)))
        notify_team(conv, reason='new' if first_user_message else 'message')
        return replies

    # Nobody available: honest automated help + a way to get a human reply later.
    answer = automated_answer(
        text, page_url=conv.page_url, contact_captured=contact_captured,
    )
    facts_rt = _site_facts()['response_time']
    if answer:
        replies.append(add_message(conv, 'bot', answer))
    if contact_captured:
        replies.append(add_message(conv, 'system', contact_confirmation(conv)))
    elif first_user_message or not answer:
        if conv.user_email or conv.user_phone:
            note = f"Our team is offline right now. Your message is saved and a team member will reply here and by email ({facts_rt.lower()})."
        else:
            note = (f"Our team is offline right now, but a real person reads every message ({facts_rt.lower()}). "
                    "Leave your email or WhatsApp number below so we can reply even if you close this page.")
        replies.append(add_message(conv, 'system', note))
    notify_team(conv, reason='new' if first_user_message else 'message')
    return replies


def maybe_waiting_followup(conv):
    """If nobody picked up a waiting chat in time, tell the visitor honestly (once)."""
    if conv.mode != 'waiting' or conv.followup_prompted or not conv.waiting_since:
        return None
    if timezone.now() - conv.waiting_since < timedelta(seconds=WAITING_FOLLOWUP_SECONDS):
        return None
    conv.followup_prompted = True
    conv.save(update_fields=['followup_prompted'])
    if conv.user_email or conv.user_phone:
        text = "Sorry for the wait — the team is busy. Your message is saved, and a real ProjectsHub team member will follow up within 24 hours."
    else:
        text = ("Sorry for the wait — the team is busy. Leave your email or WhatsApp number below, "
                "and a real ProjectsHub team member will follow up within 24 hours.")
    return add_message(conv, 'system', text)


# ── Email notifications ───────────────────────────────────────────────────────

def _send(subject, body, recipients, reply_to=None):
    recipients = [r for r in recipients if r]
    if not recipients:
        return

    def _do():
        try:
            from django.core.mail import EmailMessage
            EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, recipients,
                         reply_to=[reply_to] if reply_to else None).send(fail_silently=True)
        except Exception:
            logger.exception('live_chat: email send failed')

    if getattr(settings, 'CHAT_EMAIL_ASYNC', True):
        threading.Thread(target=_do, daemon=True).start()
    else:
        _do()


def _site_base():
    return getattr(settings, 'CANONICAL_SITE_URL', '') or 'https://projectshub.co.in'


def notify_team(conv, reason='new'):
    """Email the team about a chat that needs a human — at most once per 15 minutes per chat,
    and only when no agent is actively watching the inbox."""
    now = timezone.now()
    if online_agents() and reason != 'new':
        return
    if conv.team_notified_at and now - conv.team_notified_at < timedelta(minutes=15):
        return
    recipients = getattr(settings, 'CHAT_NOTIFY_EMAILS', None) or [settings.DEFAULT_FROM_EMAIL]
    last = conv.messages.filter(sender='user').order_by('-timestamp').first()
    who = conv.user_name or conv.user_email or 'A website visitor'
    body = (
        f"{who} is waiting on live chat.\n\n"
        f"Latest message:\n{last.message if last else ''}\n\n"
        f"Page: {conv.page_url}\n"
        f"Contact: {conv.user_email or '-'} / {conv.user_phone or '-'}\n\n"
        f"Reply now: {_site_base()}/admin/live-chat/?c={conv.pk}\n"
    )
    ChatbotConversation.objects.filter(pk=conv.pk).update(team_notified_at=now)
    conv.team_notified_at = now
    _send(f"[Live chat] {who} needs a reply", body, recipients, reply_to=conv.user_email or None)


def email_visitor_if_away(conv, msg):
    """Forward a team reply by email when the visitor has left the page."""
    now = timezone.now()
    if not conv.user_email:
        return False
    if conv.visitor_last_seen and now - conv.visitor_last_seen < timedelta(seconds=VISITOR_ONLINE_SECONDS):
        return False
    if conv.visitor_emailed_at and now - conv.visitor_emailed_at < VISITOR_EMAIL_COOLDOWN:
        return False
    agent = agent_public(msg.agent) or {'name': 'The ProjectsHub team'}
    body = (
        f"Hi {conv.user_name or 'there'},\n\n"
        f"{agent['name']} from ProjectsHub replied to your chat:\n\n"
        f"{msg.message}\n\n"
        f"Reply to this email or continue the chat on the website: {_site_base()}/?chat=open\n\n"
        f"— ProjectsHub\n"
    )
    ChatbotConversation.objects.filter(pk=conv.pk).update(visitor_emailed_at=now)
    conv.visitor_emailed_at = now
    support = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    _send('New reply from ProjectsHub', body, [conv.user_email], reply_to=support)
    return True


def visitor_is_online(conv, now=None):
    now = now or timezone.now()
    return bool(conv.visitor_last_seen and now - conv.visitor_last_seen < timedelta(seconds=VISITOR_ONLINE_SECONDS))


def inbox_queryset(filter_name, user, q=''):
    """Conversations for the agent inbox. 'waiting' means *needs a human reply*: the visitor's
    latest message has not been answered by a team member (automated answers don't count)."""
    from django.db.models import Max, Value
    from django.db.models.functions import Coalesce
    qs = ChatbotConversation.objects.annotate(
        last_user_id=Max('messages__id', filter=Q(messages__sender='user')),
        last_agent_id=Coalesce(Max('messages__id', filter=Q(messages__sender='agent')), Value(0)),
    ).filter(last_user_id__isnull=False)
    if filter_name == 'waiting':
        from django.db.models import F
        qs = qs.filter(last_user_id__gt=F('last_agent_id')).exclude(status__in=['resolved', 'archived'])
    elif filter_name == 'mine':
        qs = qs.filter(assigned_agent=user).exclude(status__in=['resolved', 'archived'])
    elif filter_name == 'resolved':
        qs = qs.filter(status__in=['resolved', 'archived'])
    elif filter_name == 'open':
        qs = qs.exclude(status__in=['resolved', 'archived'])
    if q:
        match_ids = ChatbotConversation.objects.filter(
            Q(user_name__icontains=q) | Q(user_email__icontains=q) | Q(user_phone__icontains=q) |
            Q(messages__message__icontains=q)
        ).values('id')
        qs = qs.filter(id__in=match_ids)
    return qs.select_related('assigned_agent').order_by('-last_message_at', '-updated_at')
