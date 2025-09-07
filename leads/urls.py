# leads/urls.py
from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    
    path('contact/thank-you/', views.contact_thank_you, name='contact_thank_you'),
    path('landlords/thank-you/', views.landlord_thank_you, name='landlord_thank_you'),
    
    # CRM views (login required)
    path('', views.lead_dashboard, name='lead_dashboard'),
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<int:pk>/delete/', views.lead_delete, name='lead_delete'),
    path('leads/<int:pk>/quick-update/', views.lead_quick_update, name='lead_quick_update'),
    
    # Bulk actions and export
    path('leads/bulk-action/', views.lead_bulk_action, name='lead_bulk_action'),
    path('leads/export/', views.lead_export, name='lead_export'),
    
    # Activities
    path('activities/', views.activity_list, name='activity_list'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]