# Group Chat Feature

This document explains the group chat functionality added to the Project Review System.

## Overview
- Each `ProjectGroup` has a dedicated chat room.
- Teachers assigned to the group, its student members, and admins can read/send messages.
- Uses Django views with AJAX polling (no extra realtime infra required).

## Data Model
- `ChatRoom` (one-to-one with `ProjectGroup`)
- `ChatMessage` (FK to `ChatRoom`, FK to `CustomUser`, text, timestamp)

Location: `project_review_app/models.py`

## URLs
Added in `project_review_app/urls.py`:
- `GET  /chat/group/<group_id>/` → chat page (HTML)
- `GET  /chat/room/<room_id>/messages/?since=<id>` → JSON polling
- `POST /chat/room/<room_id>/send/` → send message (JSON)

## Views
Defined in `project_review_app/views.py`:
- `group_chat(group_id)` → ensures room exists and renders page
- `chat_messages(room_id)` → returns messages, supports `?since=`
- `chat_send(room_id)` → validates access, creates `ChatMessage`

Access control (all):
- Group teacher OR group student member OR admin

## Templates & UI
- Page: `templates/chat/group_chat.html`
  - Nude palette styling to match app
  - Polls every 1.5s, posts with CSRF
- Entry points:
  - Student: `templates/student/my_group.html` → “Open Chat” button
  - Teacher: `templates/teacher/group_detail.html` → “Open Group Chat” button

## Flow
1) Open `/chat/group/<group_id>/` → room auto-created
2) Poll `/chat/room/<room_id>/messages/?since=<last_id>`
3) Send via `/chat/room/<room_id>/send/` (POST `text`)
4) UI appends and autoscrolls

## Setup
```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

## Security Notes
- All endpoints `@login_required`
- Per-request authorization enforced
- Basic client-side escaping when injecting message text

## Future Enhancements
- WebSockets (Django Channels) for realtime
- Attachments, typing indicators, read receipts
- Notifications

## Troubleshooting
- 400/403: verify user is teacher/member/admin of the group
- No messages: check Network tab for calls to `/chat/room/<id>/messages/`
- CSRF errors on send: ensure CSRF token is included

---

## Code Explanation

### Models
```python
# project_review_app/models.py
class ChatRoom(models.Model):
    group = models.OneToOneField(ProjectGroup, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
```
- `ChatRoom` binds one room per `ProjectGroup` using `OneToOneField`.
- `ChatMessage` stores the message text, author (`sender`) and timestamp; messages are ordered chronologically by default.

### URLs
```python
# project_review_app/urls.py
path('chat/group/<int:group_id>/', views.group_chat, name='group_chat'),
path('chat/room/<int:room_id>/messages/', views.chat_messages, name='chat_messages'),
path('chat/room/<int:room_id>/send/', views.chat_send, name='chat_send'),
```
- Three routes: page render, polling API, and send API.

### Views (server-side logic)
```python
# project_review_app/views.py
@login_required
def group_chat(request, group_id):
    group = get_object_or_404(ProjectGroup, id=group_id)
    # authorize: teacher/admin or student member
    is_teacher = (request.user.role == 'teacher' and group.teacher_id == request.user.id)
    is_member = GroupMember.objects.filter(group=group, student=request.user).exists()
    if not (is_teacher or is_member or request.user.role == 'admin'):
        raise PermissionDenied
    room, _ = ChatRoom.objects.get_or_create(group=group)
    return render(request, 'chat/group_chat.html', {'group': group, 'room': room})
```
- Ensures only authorized users can enter the room and lazily creates `ChatRoom` for the group.

```python
@login_required
def chat_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    group = room.group
    # same access control as page view
    is_teacher = (request.user.role == 'teacher' and group.teacher_id == request.user.id)
    is_member = GroupMember.objects.filter(group=group, student=request.user).exists()
    if not (is_teacher or is_member or request.user.role == 'admin'):
        return HttpResponseBadRequest('Not allowed')

    since = request.GET.get('since')
    qs = room.messages.select_related('sender')
    if since:
        qs = qs.filter(id__gt=since)

    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'sender_role': m.sender.role,
        'text': m.text,
        'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_me': m.sender_id == request.user.id,
    } for m in qs.order_by('id')]
    last_id = data[-1]['id'] if data else int(since or 0)
    return JsonResponse({'messages': data, 'last_id': last_id})
```
- Supports incremental fetching via `?since=<last_id>` to minimize payload.

```python
@login_required
def chat_send(request, room_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    room = get_object_or_404(ChatRoom, id=room_id)
    group = room.group
    is_teacher = (request.user.role == 'teacher' and group.teacher_id == request.user.id)
    is_member = GroupMember.objects.filter(group=group, student=request.user).exists()
    if not (is_teacher or is_member or request.user.role == 'admin'):
        return HttpResponseBadRequest('Not allowed')

    text = (request.POST.get('text') or '').strip()
    if not text:
        return HttpResponseBadRequest('Empty')

    msg = ChatMessage.objects.create(room=room, sender=request.user, text=text)
    return JsonResponse({
        'id': msg.id,
        'sender': msg.sender.username,
        'sender_role': msg.sender.role,
        'text': msg.text,
        'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_me': True,
    })
```
- Validates HTTP method and input, enforces authorization again, persists new message, responds with the created message payload.

### Template & Frontend Logic
```html
<!-- templates/chat/group_chat.html (excerpt) -->
<div id="chatBody" class="chat-body"></div>
<div class="chat-input">
  <input id="msgInput" type="text" placeholder="Type your message..." />
  <button id="sendBtn"><i class="bi bi-send"></i> Send</button>
</div>
<script>
  const roomId = {{ room.id }};
  let lastId = 0;
  async function fetchMessages() {
    const res = await fetch('{% url 'chat_messages' 0 %}'.replace('/0/', `/${roomId}/`) + `?since=${lastId}`);
    if (!res.ok) return;
    const data = await res.json();
    if (data.messages.length) {
      const body = document.getElementById('chatBody');
      data.messages.forEach(m => {
        const el = document.createElement('div');
        el.className = 'msg ' + (m.is_me ? 'me' : 'other');
        el.innerHTML = `<div>${m.text.replace(/</g,'&lt;')}</div><div class="msg-meta">${m.sender} • ${m.created_at}</div>`;
        body.appendChild(el);
      });
      lastId = data.last_id || lastId;
      body.scrollTop = body.scrollHeight;
    }
  }
  async function sendMessage() {
    const input = document.getElementById('msgInput');
    const text = input.value.trim();
    if (!text) return;
    const res = await fetch('{% url 'chat_send' 0 %}'.replace('/0/', `/${roomId}/`), {
      method: 'POST',
      headers: { 'X-CSRFToken': '{{ csrf_token }}' },
      body: new URLSearchParams({ text })
    });
    if (res.ok) { input.value = ''; fetchMessages(); }
  }
  document.getElementById('sendBtn').addEventListener('click', sendMessage);
  document.getElementById('msgInput').addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });
  setInterval(fetchMessages, 1500);
  fetchMessages();
</script>
```
- Polls new messages every 1.5s.
- Sends messages via `fetch` POST with CSRF header.
- Escapes `<` to reduce XSS risk when injecting message text into the DOM.
