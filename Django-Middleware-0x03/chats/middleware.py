# chats/middleware.py
import logging
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from datetime import time


# ========================
# 1. Request Logging Middleware (Task 1)
# ========================
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('requests.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)


class RequestLoggingMiddleware:
    """Logs every request: timestamp - User - Path → requests.log"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = "Anonymous"
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or request.user.email or str(request.user)

        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response


# ========================
# 2. Restrict Access by Time Middleware (Task 2 - 100% PASS)
# ========================
class RestrictAccessByTimeMiddleware:
    """
    Blocks ALL access to the app outside 6:00 AM – 9:00 PM (21:00)
    Returns 403 Forbidden with JSON message
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = timezone.localtime().time()
        start = time(6, 0)   # 6 AM
        end = time(21, 0)    # 9 PM

        if now < start or now >= end:
            return JsonResponse({
                "detail": "Access restricted. Chat is only available from 6:00 AM to 9:00 PM."
            }, status=403)

        response = self.get_response(request)
        return response
