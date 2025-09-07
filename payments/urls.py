
# ================================
# URLS.PY - Complete URL configuration
# ================================

# urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Payment URLs
    path('payments/', views.payment_list_view, name='payment_list'),
    path('payments/create/', views.payment_create_view, name='payment_create'),
   
]
    