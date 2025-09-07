# support/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import SupportCategory, SupportTicket, TicketComment

@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority_level', 'sla_hours', 'ticket_count']
    list_filter = ['priority_level']
    search_fields = ['name', 'description']
    ordering = ['priority_level', 'name']
    
    def ticket_count(self, obj):
        count = obj.supportticket_set.count()
        if count > 0:
            url = reverse('admin:support_supportticket_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} tickets</a>', url, count)
        return '0 tickets'
    ticket_count.short_description = 'Tickets'

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    fields = ['author', 'comment_type', 'comment', 'is_internal', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['created_at']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_id', 'subject', 'resident_name', 'category', 
        'priority_display', 'status_display', 'assigned_to', 
        'overdue_status', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'assigned_to', 
        'created_at', 'resolved_at'
    ]
    search_fields = [
        'ticket_id', 'subject', 'description', 
        'resident__user__first_name', 'resident__user__last_name',
        'resident__user__email'
    ]
    readonly_fields = [
        'ticket_id', 'created_at', 'updated_at', 'resolved_at', 
        'closed_at', 'first_response_time', 'is_overdue'
    ]
    fieldsets = (
        ('Ticket Information', {
            'fields': (
                'ticket_id', 'resident', 'property_ref', 'room',
                'category', 'subject', 'description'
            )
        }),
        ('Priority & Assignment', {
            'fields': (
                'priority', 'status', 'assigned_to'
            )
        }),
        ('SLA Tracking', {
            'fields': (
                'sla_due_date', 'first_response_time', 
                'resolution_time', 'is_overdue'
            )
        }),
        ('Resolution', {
            'fields': (
                'resolution_notes', 'resolved_by', 'resolved_at', 'closed_at'
            )
        }),
        ('Cost Tracking', {
            'fields': (
                'estimated_cost', 'actual_cost'
            )
        }),
        ('Follow-up', {
            'fields': (
                'requires_followup', 'followup_date'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            )
        })
    )
    inlines = [TicketCommentInline]
    date_hierarchy = 'created_at'
    ordering = ['priority', '-created_at']
    
    def resident_name(self, obj):
        return obj.resident.user.get_full_name()
    resident_name.short_description = 'Resident'
    resident_name.admin_order_field = 'resident__user__first_name'
    
    def priority_display(self, obj):
        colors = {1: 'red', 2: 'orange', 3: 'blue', 4: 'green'}
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    priority_display.admin_order_field = 'priority'
    
    def status_display(self, obj):
        colors = {
            'open': 'red',
            'in_progress': 'orange', 
            'waiting_resident': 'blue',
            'escalated': 'purple',
            'resolved': 'green',
            'closed': 'gray'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def overdue_status(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">OVERDUE</span>'
            )
        return 'On Time'
    overdue_status.short_description = 'SLA Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'resident__user', 'category', 'assigned_to__user', 
            'property_ref', 'room'
        )

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'author', 'comment_type', 'is_internal', 
        'created_at', 'comment_preview'
    ]
    list_filter = ['comment_type', 'is_internal', 'created_at']
    search_fields = ['ticket__ticket_id', 'comment', 'author__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'ticket', 'author__user'
        )