# urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "dashboard"

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    path('profile/notification-settings/', views.notification_settings_view, name='notification_settings'),
]