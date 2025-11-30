from django.urls import path
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_user'),
    path('thread/<int:message_id>/', views.conversation_thread, name='conversation_thread'),
]
