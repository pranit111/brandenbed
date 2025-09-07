# landlords/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Landlord, LandlordDocument

class LandlordDocumentInline(admin.TabularInline):
    model = LandlordDocument
    extra = 0
    fields = ['document_type', 'title', 'file', 'uploaded_at', 'uploaded_by']
    readonly_fields = ['uploaded_at', 'uploaded_by']
    ordering = ['-uploaded_at']

@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = [
        'landlord_id', 'landlord_name', 'email', 'landlord_type',
        'partnership_status_display', 'total_properties', 'total_earnings_display',
        'assigned_bd_executive', 'created_at'
    ]
    list_filter = [
        'partnership_status', 'landlord_type', 'assigned_bd_executive',
        'guaranteed_rent_preference', 'created_at', 'partnership_start_date'
    ]
    search_fields = [
        'landlord_id', 'user__first_name', 'user__last_name', 
        'user__email', 'company_name', 'tax_id'
    ]
    readonly_fields = [
        'landlord_id', 'total_properties', 'total_earnings_to_date',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'landlord_id', 'user', 'landlord_type', 'company_name', 'tax_id'
            )
        }),
        ('Partnership Details', {
            'fields': (
                'partnership_status', 'partnership_start_date', 'assigned_bd_executive'
            )
        }),
        ('Financial Information', {
            'fields': (
                'preferred_payout_schedule', 'bank_account_number', 
                'bank_name', 'iban', 'total_earnings_to_date'
            )
        }),
        ('Preferences', {
            'fields': (
                'guaranteed_rent_preference', 'maintenance_handling',
                'preferred_communication'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'total_properties',
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            )
        })
    )
    inlines = [LandlordDocumentInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def landlord_name(self, obj):
        if obj.company_name:
            return f"{obj.user.get_full_name()} ({obj.company_name})"
        return obj.user.get_full_name()
    landlord_name.short_description = 'Name'
    landlord_name.admin_order_field = 'user__first_name'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    email.admin_order_field = 'user__email'
    
    def partnership_status_display(self, obj):
        colors = {
            'prospect': 'blue',
            'under_evaluation': 'orange',
            'active': 'green',
            'inactive': 'gray',
            'terminated': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.partnership_status, 'black'),
            obj.get_partnership_status_display()
        )
    partnership_status_display.short_description = 'Partnership Status'
    partnership_status_display.admin_order_field = 'partnership_status'
    
    def total_earnings_display(self, obj):
        if obj.total_earnings_to_date:
            return f"€{obj.total_earnings_to_date:,.2f}"
        return "€0.00"
    total_earnings_display.short_description = 'Total Earnings'
    total_earnings_display.admin_order_field = 'total_earnings_to_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'assigned_bd_executive__user'
        ).prefetch_related('properties')
    
    actions = ['activate_partnership', 'deactivate_partnership', 'export_landlords']
    
    def activate_partnership(self, request, queryset):
        updated = queryset.update(
            partnership_status='active',
            partnership_start_date=timezone.now().date()
        )
        self.message_user(
            request, 
            f'{updated} landlord(s) activated successfully.'
        )
    activate_partnership.short_description = "Activate selected partnerships"
    
    def deactivate_partnership(self, request, queryset):
        updated = queryset.update(partnership_status='inactive')
        self.message_user(
            request, 
            f'{updated} landlord(s) deactivated successfully.'
        )
    deactivate_partnership.short_description = "Deactivate selected partnerships"
    
    def export_landlords(self, request, queryset):
        # This would trigger the export functionality
        # You can implement CSV export here or redirect to export view
        self.message_user(
            request,
            f'Export functionality for {queryset.count()} landlord(s) would be triggered here.'
        )
    export_landlords.short_description = "Export selected landlords"

@admin.register(LandlordDocument)
class LandlordDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'landlord', 'document_type', 'title', 'uploaded_at', 
        'uploaded_by', 'file_size'
    ]
    list_filter = ['document_type', 'uploaded_at', 'uploaded_by']
    search_fields = [
        'landlord__landlord_id', 'landlord__user__first_name',
        'landlord__user__last_name', 'title'
    ]
    readonly_fields = ['uploaded_at', 'file_size']
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']
    
    def file_size(self, obj):
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "No file"
    file_size.short_description = 'File Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'landlord__user', 'uploaded_by__user'
        )

# Custom admin site configurations
admin.site.site_header = "BrandenBed CRM Administration"
admin.site.site_title = "BrandenBed CRM Admin"
admin.site.index_title = "Welcome to BrandenBed CRM Administration"