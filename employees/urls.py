# employees/urls.py
from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee URLs
    path('', views.employee_list, name='employee_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),
    path('hierarchy/', views.employee_hierarchy, name='employee_hierarchy'),
    path('export/', views.employee_export, name='employee_export'),
    
    # Role URLs
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/', views.role_detail, name='role_detail'),
    path('roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    path('roles/<int:pk>/permissions-preview/', views.role_permissions_preview, name='role_permissions_preview'),
]