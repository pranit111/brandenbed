
# ================================
# URLS.PY - Complete URL configuration
# ================================

# urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Maintenance URLs
    path('maintenance/create/', views.maintenance_request_create_view, name='maintenance_request_create'),

]
    