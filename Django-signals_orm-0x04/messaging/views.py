from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json


@login_required
@require_POST
def delete_user(request):
    """
    View to allow a user to delete their own account.
    The actual cleanup is done via post_delete signal (see signals.py)
    """
    try:
        user = request.user
        user.delete()  # This will trigger the post_delete signal
        return JsonResponse({"status": "success", "message": "Account deleted successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
