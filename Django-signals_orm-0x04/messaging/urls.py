from django.urls import path
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_user'),
]
