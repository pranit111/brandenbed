# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('properties/', views.PropertiesView.as_view(), name='properties'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('landlords/', views.LandlordsView.as_view(), name='landlords'),
]