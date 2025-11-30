from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import cache_page
from .models import Message


@login_required
@require_POST
def delete_user(request):
    request.user.delete()
    return JsonResponse({"status": "success"})


@cache_page(60)
@login_required
@require_GET
def message_list(request):
    """Cached view — returns all messages for the user (inbox + sent)"""
    messages = Message.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by('-timestamp')[:50]

    data = [
        {
            "id": m.id,
            "sender": m.sender.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
            "is_read": m.is_read,
        }
        for m in messages
    ]
    return JsonResponse({"messages": data})


@login_required
@require_GET
def unread_messages(request):
    messages = Message.unread.unread_for_user(request.user).only('id', 'sender', 'content', 'timestamp')
    data = [{"id": m.id, "sender": m.sender.username, "content": m.content} for m in messages]
    return JsonResponse({"unread_messages": data})


@login_required
@require_GET
def conversation_thread(request, message_id):
    Message.objects.filter(sender=request.user).exists()
    root = Message.objects.select_related('sender').prefetch_related('replies').get(id=message_id, receiver=request.user)
    def build(m): return [{"id": m.id, "sender": m.sender.username, "content": m.content}] + [i for r in m.replies.all() for i in build(r)]
    return JsonResponse({"thread": build(root)})
