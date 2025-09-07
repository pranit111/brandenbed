# support/urls.py
from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Dashboard and main views
    path('', views.SupportDashboardView.as_view(), name='support_dashboard'),
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<str:ticket_id>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    
    # Ticket actions
    path('tickets/<str:ticket_id>/update/', views.ticket_update, name='ticket_update'),
    path('tickets/<str:ticket_id>/comment/', views.add_comment, name='add_comment'),
    path('tickets/<str:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    
    # Specialized views
    path('tickets/overdue/', views.OverdueTicketsView.as_view(), name='overdue_tickets'),
    path('tickets/export/', views.export_tickets, name='export_tickets'),
    
    # Bulk actions
    path('tickets/bulk/assign/', views.bulk_assign_tickets, name='bulk_assign'),
    
    # API endpoints
    path('api/stats/', views.ticket_stats_api, name='ticket_stats_api'),
    
    # Support Category Management
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Bulk operations for categories
    path('categories/bulk/sla-update/', views.bulk_update_category_sla, name='bulk_update_category_sla'),
    
    # API endpoints for categories
    path('api/categories/stats/', views.category_stats_api, name='category_stats_api'),
]