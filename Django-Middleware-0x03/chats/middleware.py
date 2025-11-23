# chats/middleware.py
import logging
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from datetime import time
from collections import defaultdict
import time as time_module


# ========================
# Logger Setup
# ========================
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

handler = logging.FileHandler('requests.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)


# ========================
# 1. Request Logging Middleware
# ========================
class RequestLoggingMiddleware:
    """
    Logs every request: timestamp - User - Path → requests.log
    """
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
# 2. Restrict Access by Time Middleware
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
# 3. Offensive Language Middleware (Rate Limiting)
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


# ========================
# 4. Role Permission Middleware
# ========================
class RolePermissionMiddleware:
    """
    Checks user's role before allowing access to specific actions
    Only allows admin or moderator users for protected actions
    Excludes Django admin paths to avoid conflicts with built-in admin auth
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Define protected actions and paths (custom app routes only)
        self.protected_actions = [
            '/moderate/',    # Moderation actions
            '/delete/',      # Delete operations  
            '/manage/',      # Management operations
            '/users/',       # User management
            '/api/admin/',   # Custom API admin routes
            '/chat-admin/',  # Custom chat admin routes
        ]

    def __call__(self, request):
        # Check if the current path requires admin/moderator permissions
        if self.requires_permission(request.path):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    "detail": "Authentication required to access this resource."
                }, status=401)
            
            # Check if user has required role (admin or moderator)
            if not self.has_required_role(request.user):
                return JsonResponse({
                    "detail": "Access denied. Admin or moderator role required."
                }, status=403)

        response = self.get_response(request)
        return response

    def requires_permission(self, path):
        """
        Check if the requested path requires admin/moderator permissions
        Excludes Django admin paths to let Django's built-in admin handle authentication
        """
        # Skip Django admin paths completely
        if path.startswith('/admin/'):
            return False
            
        # Skip admin login and logout pages
        if path in ['/admin/login/', '/admin/logout/']:
            return False
            
        # Check if path starts with any of the protected action prefixes
        return any(path.startswith(protected_path) for protected_path in self.protected_actions)

    def has_required_role(self, user):
        """
        Check if user has admin or moderator role
        Supports multiple role checking methods
        """
        # Method 1: Check Django's built-in staff/superuser flags
        if hasattr(user, 'is_staff') and user.is_staff:
            return True
        if hasattr(user, 'is_superuser') and user.is_superuser:
            return True
        
        # Method 2: Check Django groups
        if hasattr(user, 'groups'):
            try:
                group_names = user.groups.values_list('name', flat=True)
                if 'admin' in group_names or 'moderator' in group_names:
                    return True
            except:
                pass
        
        # Method 3: Check custom role field (if exists)
        if hasattr(user, 'role'):
            if user.role in ['admin', 'moderator']:
                return True
        
        # Method 4: Check specific permissions
        if hasattr(user, 'has_perm'):
            if user.has_perm('chats.admin_access') or user.has_perm('chats.moderator_access'):
                return True
            # Check Django's default admin permissions
            if user.has_perm('auth.admin_access') or user.has_perm('auth.moderator_access'):
                return True
        
        return False
