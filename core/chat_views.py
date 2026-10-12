"""
Live chat HTTP endpoints.

Visitor API (public, authenticated by the per-conversation secret token, so CSRF-exempt):
    GET  /api/chat/presence/          team availability for the launcher/header
    POST /api/chat/session/           resume a conversation (history + state)
    POST /api/chat/message/           send a visitor message (creates the conversation on first send)
    GET  /api/chat/poll/              new messages + typing/read state since ?after=<id>
    POST /api/chat/typing/            visitor typing signal
    POST /api/chat/profile/           visitor name / email / phone
    POST /api/chat/request-human/     ask for a team member

Agent API (staff with core.change_chatbotconversation, CSRF-protected):
    /admin/live-chat/                 inbox page
    /admin/api/chat/...               inbox, thread, reply, typing, status, presence
"""
import json
import logging
import re
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from . import live_chat as lc
from .models import ChatAgentStatus, ChatbotConversation, ChatbotMessage

logger = logging.getLogger(__name__)

IP_MESSAGES_PER_MINUTE = 30
CONVERSATION_MESSAGES_PER_MINUTE = 15
NEW_CONVERSATIONS_PER_HOUR = 40
PHONE_RE = re.compile(r'^[0-9+()\-\s]{7,25}$')


def _client_ip(request):
    from .views import get_client_ip
    return get_client_ip(request)


def _data(request):
    if request.method == 'GET':
        return request.GET
    if request.content_type and 'application/json' in request.content_type:
        try:
            body = json.loads(request.body or b'{}')
            return body if isinstance(body, dict) else {}
        except (ValueError, UnicodeDecodeError):
            return {}
    return request.POST


def _str(data, key, limit=None):
    val = data.get(key, '')
    val = val.strip() if isinstance(val, str) else ''
    return val[:limit] if limit else val


def _err(message, status=400, **extra):
    payload = {'success': False, 'error': message}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def _hit(key, limit, window):
    """Fixed-window counter. Returns True when the limit is exceeded."""
    count = cache.get(key, 0)
    if count >= limit:
        return True
    cache.set(key, count + 1, window)
    return False


def _auth(request, data):
    conv = lc.get_conversation(_str(data, 'session_id'), _str(data, 'token'))
    if conv is None:
        return None, _err('Chat session not found. Please start a new chat.', status=403, reset=True)
    return conv, None


def _touch_visitor(conv, read_upto=None):
    fields = {'visitor_last_seen': timezone.now()}
    if read_upto and read_upto > conv.visitor_last_read_id:
        fields['visitor_last_read_id'] = read_upto
    ChatbotConversation.objects.filter(pk=conv.pk).update(**fields)
    for k, v in fields.items():
        setattr(conv, k, v)


def _visible_messages(conv, after=0):
    return list(
        conv.messages.select_related('agent', 'agent__chat_status').filter(id__gt=after).order_by('id')[:200]
    )


def _db_safe(view):
    """Return a clear JSON error (instead of an HTML 500) if the chat tables are missing
    or the database is unavailable, e.g. when `manage.py migrate` hasn't been run."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except DatabaseError:
            logger.exception('Live chat database error (have migrations been applied?)')
            return JsonResponse({'success': False, 'error': 'Live chat is temporarily unavailable. '
                                 'Please message us on WhatsApp instead.'}, status=503)
    return wrapper


# ── Visitor endpoints ─────────────────────────────────────────────────────────

@require_GET
@_db_safe
def chat_presence(request):
    data = cache.get('live_chat_presence')
    if data is None:
        data = lc.team_presence()
        cache.set('live_chat_presence', data, 10)
    return JsonResponse({'success': True, 'team': data})


@csrf_exempt
@require_POST
@_db_safe
def chat_session(request):
    data = _data(request)
    conv = lc.get_conversation(_str(data, 'session_id'), _str(data, 'token'))
    if conv is None:
        return JsonResponse({'success': True, 'session': None, 'team': lc.team_presence()})
    _touch_visitor(conv)
    msgs = _visible_messages(conv)
    return JsonResponse({
        'success': True,
        'session': {'session_id': conv.session_id},
        'messages': [lc.serialize_message(m) for m in msgs],
        'state': lc.conversation_state(conv),
        'team': lc.team_presence(),
    })


@csrf_exempt
@require_POST
@_db_safe
def chat_message(request):
    data = _data(request)
    text = _str(data, 'message')
    if not text:
        return _err('message cannot be empty')
    if len(text) > lc.MAX_MESSAGE_LENGTH:
        return _err(f'Message exceeds maximum allowed length of {lc.MAX_MESSAGE_LENGTH} characters.')

    ip = _client_ip(request) or 'unknown'
    if _hit(f'chat_rate:{ip}', IP_MESSAGES_PER_MINUTE, 60):
        return _err('Rate limit exceeded. Please wait a minute.', status=429)

    client_id = _str(data, 'client_id', 64)
    page_url = (_str(data, 'page_url', 500) or request.META.get('HTTP_REFERER', '/'))[:500]
    created = False
    conv = None
    if _str(data, 'token'):
        conv = lc.get_conversation(_str(data, 'session_id'), _str(data, 'token'))
        if conv is None:
            return _err('Chat session not found. Please start a new chat.', status=403, reset=True)
    if conv is None:
        if _hit(f'chat_new:{ip}', NEW_CONVERSATIONS_PER_HOUR, 3600):
            return _err('Rate limit exceeded. Please try again later.', status=429)
        session_id, token = lc.new_session_credentials()
        conv = ChatbotConversation.objects.create(
            session_id=session_id, visitor_token=token, page_url=page_url, ip_address=ip if ip != 'unknown' else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000], status='active', mode='bot',
        )
        created = True

    # Idempotent retries: same client_id → return the original message.
    if client_id:
        existing = conv.messages.filter(client_id=client_id, sender='user').first()
        if existing:
            return JsonResponse({'success': True, 'message': lc.serialize_message(existing), 'replies': [],
                                 'state': lc.conversation_state(conv)})

    window_start = timezone.now() - timedelta(seconds=60)
    if conv.messages.filter(sender='user', timestamp__gte=window_start).count() >= CONVERSATION_MESSAGES_PER_MINUTE:
        return _err('You are sending messages too quickly. Please wait a moment.', status=429)

    if page_url and conv.page_url != page_url:
        conv.page_url = page_url
        conv.save(update_fields=['page_url'])

    first = not conv.messages.filter(sender='user').exists()
    msg = lc.add_message(conv, 'user', text, client_id=client_id)
    _capture_contact_from_text(conv, text)
    _touch_visitor(conv)
    ChatbotConversation.objects.filter(pk=conv.pk).update(visitor_typing_until=None)

    replies = lc.handle_visitor_message(conv, text, first_user_message=first)
    payload = {
        'success': True,
        'message': lc.serialize_message(msg),
        'replies': [lc.serialize_message(r) for r in replies],
        'state': lc.conversation_state(conv),
        # legacy keys kept for older clients / tests
        'conversation_id': conv.id,
        'message_id': msg.id,
        'status': conv.status,
        'is_lead': conv.status == 'lead',
    }
    if created:
        payload['session'] = {'session_id': conv.session_id, 'token': conv.visitor_token}
    return JsonResponse(payload)


def _capture_contact_from_text(conv, text):
    changed = []
    if not conv.user_email:
        m = re.search(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+', text)
        if m:
            try:
                validate_email(m.group(0))
                conv.user_email = m.group(0)[:254]
                changed.append('user_email')
            except ValidationError:
                pass
    if not conv.user_phone:
        m = re.search(r'(?<!\d)(\+?\d[\d\s\-]{8,15}\d)(?!\d)', text)
        if m and len(re.sub(r'\D', '', m.group(1))) >= 10:
            conv.user_phone = m.group(1).strip()[:50]
            changed.append('user_phone')
    if changed:
        if conv.status == 'active':
            conv.status = 'lead'
            changed.append('status')
        conv.save(update_fields=changed)


@require_GET
@_db_safe
def chat_poll(request):
    data = request.GET
    conv, error = _auth(request, data)
    if error:
        return error
    try:
        after = max(0, int(data.get('after', 0)))
    except (TypeError, ValueError):
        after = 0
    followup = lc.maybe_waiting_followup(conv)
    msgs = _visible_messages(conv, after)
    read_upto = msgs[-1].id if (msgs and data.get('read') == '1') else (after if data.get('read') == '1' else None)
    _touch_visitor(conv, read_upto=read_upto)
    conv.refresh_from_db(fields=['agent_typing_until', 'agent_last_read_id', 'mode', 'status', 'assigned_agent'])
    return JsonResponse({
        'success': True,
        'messages': [lc.serialize_message(m) for m in msgs],
        'state': lc.conversation_state(conv),
        'team': cache.get('live_chat_presence') or lc.team_presence(),
        'followup': bool(followup),
    })


@csrf_exempt
@require_POST
@_db_safe
def chat_typing(request):
    data = _data(request)
    conv, error = _auth(request, data)
    if error:
        return error
    typing = str(data.get('typing', '1')).lower() in ('1', 'true', 'yes')
    until = timezone.now() + timedelta(seconds=lc.TYPING_SECONDS) if typing else None
    ChatbotConversation.objects.filter(pk=conv.pk).update(visitor_typing_until=until, visitor_last_seen=timezone.now())
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
@_db_safe
def chat_profile(request):
    data = _data(request)
    conv, error = _auth(request, data)
    if error:
        return error
    name = _str(data, 'name', 150)
    email = _str(data, 'email', 254)
    phone = _str(data, 'phone', 50)
    if not email and not phone:
        return _err('Please enter your email or WhatsApp number.')
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return _err('Please enter a valid email address.')
    if phone and not PHONE_RE.match(phone):
        return _err('Please enter a valid phone number.')
    if name:
        conv.user_name = name
    if email:
        conv.user_email = email
    if phone:
        conv.user_phone = phone
    if conv.status == 'active':
        conv.status = 'lead'
    conv.save(update_fields=['user_name', 'user_email', 'user_phone', 'status'])
    reply = lc.add_message(
        conv, 'system',
        f"Thanks{', ' + name.split()[0] if name else ''}! We'll reply here, and by "
        f"{'email' if email else 'WhatsApp/phone'} if you've left the page.",
    )
    lc.notify_team(conv, reason='contact')
    return JsonResponse({'success': True, 'replies': [lc.serialize_message(reply)], 'state': lc.conversation_state(conv)})


@csrf_exempt
@require_POST
@_db_safe
def chat_request_human(request):
    data = _data(request)
    conv, error = _auth(request, data)
    if error:
        return error
    replies = []
    if conv.mode != 'human':
        agents = lc.online_agents()
        conv.mode = 'waiting'
        conv.waiting_since = timezone.now()
        conv.followup_prompted = False
        conv.save(update_fields=['mode', 'waiting_since', 'followup_prompted'])
        if agents:
            text = f"Got it — {agents[0].public_name} from the team will join this chat shortly."
        elif conv.user_email or conv.user_phone:
            text = "The team is offline right now. A team member will reply here and by email as soon as they're back."
        else:
            text = "The team is offline right now. Leave your email or WhatsApp number below and a team member will get back to you."
        replies.append(lc.add_message(conv, 'system', text))
        lc.notify_team(conv, reason='new')
    return JsonResponse({'success': True, 'replies': [lc.serialize_message(r) for r in replies],
                         'state': lc.conversation_state(conv)})


# ── Agent (staff) endpoints ───────────────────────────────────────────────────

def _agent_guard(request):
    if not request.user.has_perm('core.change_chatbotconversation'):
        return _err('You do not have permission to use live chat.', status=403)
    return None


def _heartbeat(user):
    status, _ = ChatAgentStatus.objects.get_or_create(user=user, defaults={'display_name': user.first_name or ''})
    status.last_heartbeat = timezone.now()
    status.save(update_fields=['last_heartbeat'])
    cache.delete('live_chat_presence')
    return status


@staff_member_required(login_url='admin:login')
@ensure_csrf_cookie
def admin_live_chat_view(request):
    if not request.user.has_perm('core.change_chatbotconversation'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    try:
        status, _ = ChatAgentStatus.objects.get_or_create(
            user=request.user, defaults={'display_name': request.user.first_name or ''})
    except DatabaseError:
        from django.contrib import messages
        from django.shortcuts import redirect
        logger.exception('Live chat tables missing')
        messages.error(request, 'Live chat needs a database update. Click “Apply database update” above '
                                '(or run `python manage.py migrate`), then open Live Chat again.')
        return redirect('/admin/')
    return render(request, 'admin/live_chat.html', {
        'title': 'Live Chat',
        'agent_status': status,
        'initial_conversation': request.GET.get('c', ''),
    })


def _conv_summary(conv, user, now):
    last = conv.messages.exclude(sender='system').order_by('-id').first() or conv.messages.order_by('-id').first()
    unread = conv.messages.filter(sender='user', id__gt=conv.agent_last_read_id).count()
    last_user = getattr(conv, 'last_user_id', None)
    last_agent = getattr(conv, 'last_agent_id', None)
    if last_user is None:
        last_user = conv.messages.filter(sender='user').order_by('-id').values_list('id', flat=True).first()
        last_agent = conv.messages.filter(sender='agent').order_by('-id').values_list('id', flat=True).first() or 0
    needs_reply = bool(last_user and last_user > (last_agent or 0) and conv.status not in ('resolved', 'archived'))
    return {
        'id': conv.id,
        'name': conv.user_name or (conv.user_email.split('@')[0] if conv.user_email else f'Visitor #{conv.id}'),
        'email': conv.user_email,
        'phone': conv.user_phone,
        'initials': lc.initials(conv.user_name or conv.user_email or 'V'),
        'color': lc.avatar_color(conv.session_id),
        'mode': conv.mode,
        'status': conv.status,
        'unread': unread,
        'needs_reply': needs_reply,
        'last_text': (last.message[:90] if last else ''),
        'last_sender': last.sender if last else '',
        'last_at': last.timestamp.isoformat() if last else conv.updated_at.isoformat(),
        'visitor_online': lc.visitor_is_online(conv, now),
        'visitor_typing': bool(conv.visitor_typing_until and conv.visitor_typing_until > now),
        'assigned': lc.agent_public(conv.assigned_agent),
        'mine': conv.assigned_agent_id == user.id,
        'page_url': conv.page_url,
    }


@staff_member_required(login_url='admin:login')
@require_GET
def admin_chat_inbox(request):
    guard = _agent_guard(request)
    if guard:
        return guard
    status = _heartbeat(request.user)
    now = timezone.now()
    flt = request.GET.get('filter', 'open')
    q = request.GET.get('q', '').strip()[:100]
    convs = list(lc.inbox_queryset(flt, request.user, q)[:60])
    counts = {
        'waiting': lc.inbox_queryset('waiting', request.user).count(),
        'mine': lc.inbox_queryset('mine', request.user).count(),
        'open': lc.inbox_queryset('open', request.user).count(),
    }
    return JsonResponse({
        'success': True,
        'conversations': [_conv_summary(c, request.user, now) for c in convs],
        'counts': counts,
        'me': {'available': status.is_available, 'display_name': status.public_name, 'online': status.is_online},
        'team': lc.team_presence(),
    })


def _get_conv(pk):
    return ChatbotConversation.objects.select_related('assigned_agent').filter(pk=pk).first()


@staff_member_required(login_url='admin:login')
@require_GET
def admin_chat_thread(request, pk):
    guard = _agent_guard(request)
    if guard:
        return guard
    conv = _get_conv(pk)
    if not conv:
        return _err('Conversation not found.', status=404)
    try:
        after = max(0, int(request.GET.get('after', 0)))
    except (TypeError, ValueError):
        after = 0
    msgs = _visible_messages(conv, after)
    newest = conv.messages.order_by('-id').values_list('id', flat=True).first() or 0
    if newest > conv.agent_last_read_id:
        ChatbotConversation.objects.filter(pk=conv.pk).update(agent_last_read_id=newest)
        conv.agent_last_read_id = newest
    now = timezone.now()
    summary = _conv_summary(conv, request.user, now)
    summary.update({
        'ip_address': conv.ip_address,
        'created_at': conv.created_at.isoformat(),
        'service_interest': conv.service_interest,
        'admin_notes': conv.admin_notes,
        'visitor_last_read_id': conv.visitor_last_read_id,
        'visitor_last_seen': conv.visitor_last_seen.isoformat() if conv.visitor_last_seen else None,
    })
    return JsonResponse({'success': True, 'conversation': summary, 'messages': [lc.serialize_message(m) for m in msgs]})


@staff_member_required(login_url='admin:login')
@require_POST
def admin_chat_reply(request, pk):
    guard = _agent_guard(request)
    if guard:
        return guard
    conv = _get_conv(pk)
    if not conv:
        return _err('Conversation not found.', status=404)
    data = _data(request)
    text = _str(data, 'message')
    if not text:
        return _err('Message cannot be empty.')
    if len(text) > 4000:
        return _err('Message is too long (4000 characters max).')
    client_id = _str(data, 'client_id', 64)
    if client_id:
        existing = conv.messages.filter(client_id=client_id, sender='agent').first()
        if existing:
            return JsonResponse({'success': True, 'message': lc.serialize_message(existing)})
    status = _heartbeat(request.user)
    joined_now = conv.mode != 'human' or conv.assigned_agent_id is None
    conv.mode = 'human'
    conv.waiting_since = None
    if conv.assigned_agent_id is None:
        conv.assigned_agent = request.user
    if conv.status in ('resolved', 'archived'):
        conv.status = 'active'
    conv.agent_typing_until = None
    conv.save(update_fields=['mode', 'waiting_since', 'assigned_agent', 'status', 'agent_typing_until'])
    if joined_now and conv.assigned_agent_id == request.user.id:
        lc.add_message(conv, 'system', f"{status.public_name} from the ProjectsHub team joined the chat.")
    msg = lc.add_message(conv, 'agent', text, agent=request.user, client_id=client_id)
    msg = ChatbotMessage.objects.select_related('agent', 'agent__chat_status').get(pk=msg.pk)
    ChatbotConversation.objects.filter(pk=conv.pk).update(agent_last_read_id=msg.id)
    emailed = lc.email_visitor_if_away(conv, msg)
    return JsonResponse({'success': True, 'message': lc.serialize_message(msg), 'emailed': emailed})


@staff_member_required(login_url='admin:login')
@require_POST
def admin_chat_typing(request, pk):
    guard = _agent_guard(request)
    if guard:
        return guard
    typing = str(_data(request).get('typing', '1')).lower() in ('1', 'true', 'yes')
    until = timezone.now() + timedelta(seconds=lc.TYPING_SECONDS) if typing else None
    ChatbotConversation.objects.filter(pk=pk).update(agent_typing_until=until)
    if typing:
        status = getattr(request.user, 'chat_status', None)
        name = status.public_name if status else (request.user.first_name or request.user.get_username())
        cache.set(f'chat_typing_agent:{pk}', name, lc.TYPING_SECONDS + 2)
    return JsonResponse({'success': True})


@staff_member_required(login_url='admin:login')
@require_POST
def admin_chat_status(request, pk):
    guard = _agent_guard(request)
    if guard:
        return guard
    conv = _get_conv(pk)
    if not conv:
        return _err('Conversation not found.', status=404)
    data = _data(request)
    fields = []
    new_status = _str(data, 'status')
    if new_status:
        if new_status not in dict(ChatbotConversation.STATUS_CHOICES):
            return _err('Unknown status.')
        conv.status = new_status
        fields.append('status')
        if new_status in ('resolved', 'archived'):
            if conv.mode == 'waiting':
                conv.mode = 'bot'
                fields.append('mode')
            lc.add_message(conv, 'system', 'This chat was marked as resolved. Send a message any time to reopen it.')
    assign = _str(data, 'assign')
    if assign == 'me':
        conv.assigned_agent = request.user
        fields.append('assigned_agent')
    elif assign == 'none':
        conv.assigned_agent = None
        if conv.mode == 'human':
            conv.mode = 'waiting'
            conv.waiting_since = timezone.now()
            fields += ['mode', 'waiting_since']
        fields.append('assigned_agent')
    if 'admin_notes' in data:
        conv.admin_notes = _str(data, 'admin_notes', 5000)
        fields.append('admin_notes')
    if fields:
        conv.save(update_fields=list(dict.fromkeys(fields)))
    return JsonResponse({'success': True, 'conversation': _conv_summary(conv, request.user, timezone.now())})


@staff_member_required(login_url='admin:login')
@require_POST
def admin_chat_presence(request):
    guard = _agent_guard(request)
    if guard:
        return guard
    data = _data(request)
    status = _heartbeat(request.user)
    if 'available' in data:
        status.is_available = str(data.get('available')).lower() in ('1', 'true', 'yes')
    name = _str(data, 'display_name', 60)
    if name:
        status.display_name = name
    status.save(update_fields=['is_available', 'display_name'])
    cache.delete('live_chat_presence')
    return JsonResponse({'success': True, 'me': {'available': status.is_available, 'display_name': status.public_name,
                                                  'online': status.is_online}})
