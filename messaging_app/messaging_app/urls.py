# messaging_app/messaging_app/urls.py

from django.contrib import admin
from django.urls import path, include   # ← THIS LINE WAS MISSING!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),  # Your API endpoints
]
