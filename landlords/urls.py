# landlords/urls.py
from django.urls import path
from . import views

app_name = 'landlords'

urlpatterns = [
    # Dashboard and main views
    path('landlord_dashboard/', views.LandlordDashboardView.as_view(), name='landlord_dashboard'),
    path('landlords/', views.LandlordListView.as_view(), name='landlord_list'),
    path('landlords/create/', views.LandlordCreateView.as_view(), name='landlord_create'),
    path('landlords/<str:landlord_id>/', views.LandlordDetailView.as_view(), name='landlord_detail'),
    path('landlords/<str:landlord_id>/update/', views.LandlordUpdateView.as_view(), name='landlord_update'),
    
    # Partnership management
    path('landlords/<str:landlord_id>/partnership/', views.update_partnership_status, name='update_partnership'),
    
    # Document management
    path('landlords/<str:landlord_id>/documents/', views.DocumentListView.as_view(), name='document_list'),
    path('landlords/<str:landlord_id>/documents/upload/', views.upload_document, name='upload_document'),
    path('landlords/<str:landlord_id>/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    
    # Specialized views
    path('prospects/', views.ProspectsView.as_view(), name='prospects'),
    path('landlords/<str:landlord_id>/performance/', views.performance_report, name='performance_report'),
    
    # Bulk actions
    path('landlords/bulk/assign-bd/', views.bulk_assign_bd_executive, name='bulk_assign_bd'),
    
    # Export functionality
    path('landlords/export/', views.export_landlords, name='export_landlords'),
    
    # API endpoints
    path('api/stats/', views.landlord_stats_api, name='landlord_stats_api'),
]