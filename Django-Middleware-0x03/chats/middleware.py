# chats/middleware.py
import logging
from datetime import datetime


# Configure logger to write to requests.log in project root
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Create file handler that writes to requests.log
handler = logging.FileHandler('requests.log')
handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

# Add handler to logger (only once)
if not logger.handlers:
    logger.addHandler(handler)


class RequestLoggingMiddleware:
    """
    Middleware to log every incoming request with timestamp, user, and path.
    Logs to 'requests.log' in the project root.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user (handle anonymous users)
        user = request.user if request.user.is_authenticated else "Anonymous"

        # Log the request
        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        # Continue processing the request
        response = self.get_response(request)

        return response
