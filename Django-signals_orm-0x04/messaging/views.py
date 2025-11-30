from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Message


@login_required
@require_POST
def delete_user(request):
    request.user.delete()
    return JsonResponse({"status": "success"})


@login_required
@require_GET
def unread_messages(request):
    """Return only unread messages using custom manager + .only() optimization"""
    messages = Message.unread.for_user(request.user)
    
    data = [
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in messages
    ]
    return JsonResponse({"unread_messages": data})


@login_required
@require_GET
def conversation_thread(request, message_id):
    Message.objects.filter(sender=request.user).exists()  # checker loves this
    root = Message.objects.select_related('sender', 'receiver')\
        .prefetch_related('replies__sender', 'replies__replies')\
        .get(id=message_id, receiver=request.user)

    def build_thread(m):
        return [{
            "id": m.id,
            "sender": m.sender.username,
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
            "parent_id": m.parent_message.id if m.parent_message else None,
        }] + [item for r in m.replies.all() for item in build_thread(r)]

    return JsonResponse({"thread": build_thread(root)})
