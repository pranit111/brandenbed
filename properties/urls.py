
# ================================
# URLS.PY - Complete URL configuration
# ================================

# urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


app_name = 'properties'


urlpatterns = [
    # Property URLs
    path('properties/', views.property_list_view, name='property_list'),
    path('properties/<int:property_id>/', views.property_detail_view, name='property_detail'),
    path('properties/create/', views.property_create_view, name='property_create'),
    path('properties/<int:property_id>/edit/', views.property_update_view, name='property_update'),
    
    # Room URLs - These match what your templates expect
    path('properties/<int:property_id>/rooms/', views.room_list_view, name='room_list'),
    path('properties/<int:property_id>/rooms/create/', views.room_create_view, name='room_create'),
    path('properties/<int:property_id>/rooms/<int:room_id>/', views.room_detail_view, name='room_detail'),
    path('properties/<int:property_id>/rooms/<int:room_id>/edit/', views.room_edit_view, name='room_edit'),
    path('properties/<int:property_id>/rooms/<int:room_id>/delete/', views.room_delete_view, name='room_delete'),
    path('properties/<int:property_id>/rooms/<int:room_id>/update-status/', views.room_update_status_view, name='room_update_status'),
    path('properties/<int:property_id>/rooms/export/', views.room_export_view, name='room_export'),
  # AJAX endpoints
    path('properties/<int:property_id>/validate-room-number/', views.validate_room_number_ajax, name='validate_room_number'),
]
    