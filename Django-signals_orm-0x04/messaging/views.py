from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Message


@login_required
@require_POST
def delete_user(request):
    """Delete current user account – triggers post_delete signal"""
    try:
        request.user.delete()
        return JsonResponse({"status": "success", "message": "Account deleted"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
@require_GET
def conversation_thread(request, message_id):
    """Return full threaded conversation with optimized queries"""
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver')
                      .prefetch_related('replies__sender', 'replies__receiver'),
        id=message_id,
        receiver=request.user
    )

    thread = root_message.get_thread()

    data = [
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "parent_id": msg.parent_message.id if msg.parent_message else None,
            "edited": msg.edited,
        }
        for msg in thread
    ]

    return JsonResponse({"thread": data})
