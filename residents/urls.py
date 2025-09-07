# residents/urls.py
from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    # Dashboard
    path('', views.resident_dashboard, name='resident_dashboard'),
    path('analytics/', views.resident_analytics, name='analytics'),
    
    # Resident CRUD
    path('list/', views.resident_list, name='resident_list'),
    path('create/', views.resident_create, name='resident_create'),
    path('<str:resident_id>/', views.resident_detail, name='resident_detail'),
    path('<str:resident_id>/edit/', views.resident_edit, name='resident_edit'),
    path('<str:resident_id>/delete/', views.resident_delete, name='resident_delete'),
    
    # Contract Management
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/create/', views.contract_create, name='contract_create'),
    path('contracts/<str:contract_id>/', views.contract_detail, name='contract_detail'),
    
    # AJAX & Utilities
    path('<str:resident_id>/update-status/', views.update_resident_status, name='update_resident_status'),
    path('export/residents/', views.resident_export, name='resident_export'),
]