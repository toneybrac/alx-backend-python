# chats/middleware.py
import logging
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from datetime import time
from collections import defaultdict
import time as time_module


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


# ========================
# 3. Offensive Language Middleware (Task 3)
# ========================
class OffensiveLanguageMiddleware:
    """
    Tracks number of chat messages sent by each IP address and implements
    a time-based limit (5 messages per minute)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store IP addresses and their request timestamps
        self.ip_requests = defaultdict(list)
        # Rate limiting configuration
        self.max_requests = 5  # 5 messages
        self.time_window = 60  # 1 minute in seconds

    def __call__(self, request):
        # Only process POST requests (chat messages)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            
            if ip_address:
                current_time = time_module.time()
                
                # Clean old requests outside the time window
                self.clean_old_requests(ip_address, current_time)
                
                # Check if IP has exceeded the limit
                if len(self.ip_requests[ip_address]) >= self.max_requests:
                    return JsonResponse({
                        "detail": "Rate limit exceeded. Please wait before sending more messages."
                    }, status=429)
                
                # Add current request timestamp
                self.ip_requests[ip_address].append(current_time)
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def clean_old_requests(self, ip_address, current_time):
        """Remove requests that are outside the current time window"""
        if ip_address in self.ip_requests:
            # Keep only requests within the time window
            self.ip_requests[ip_address] = [
                timestamp for timestamp in self.ip_requests[ip_address]
                if current_time - timestamp <= self.time_window
            ]
