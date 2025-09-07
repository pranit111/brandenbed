# leads/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from . import models
from employees.models import Employee
from .models import Lead, LeadActivity, LeadSource

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'lead_type', 'status', 
                   'priority', 'assigned_to', 'days_since_created', 'created_at')
    list_filter = ('lead_type', 'status', 'priority', 'source', 'assigned_to', 
                  'created_at', 'is_converted')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 
                    'company_name', 'property_address')
    ordering = ('-created_at',)
    list_per_page = 25
    raw_id_fields = ('assigned_to',)
    autocomplete_fields = ['assigned_to']
    readonly_fields = ('days_since_created', 'days_since_last_contact', 
                      'created_at', 'updated_at', 'contact_attempts')
    date_hierarchy = 'created_at'
    list_editable = ('status', 'priority')
    list_select_related = ('assigned_to', 'assigned_to__user')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('lead_type', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        (_('Company Information (Landlords)'), {
            'fields': ('company_name',),
            'classes': ('collapse',)
        }),
        (_('Lead Source'), {
            'fields': ('source', 'source_details', 'referrer_name')
        }),
        (_('Inquiry Details'), {
            'fields': ('subject', 'message')
        }),
        (_('Property Details (Landlords)'), {
            'fields': ('property_address', 'property_type', 'number_of_rooms', 
                      'monthly_rent_expectation', 'property_description'),
            'classes': ('collapse',)
        }),
        (_('Tenant Preferences'), {
            'fields': ('preferred_location', 'budget_range', 'move_in_date'),
            'classes': ('collapse',)
        }),
        (_('Lead Management'), {
            'fields': ('status', 'priority', 'assigned_to', 'last_contact_date', 
                      'next_followup_date', 'contact_attempts')
        }),
        (_('Conversion Tracking'), {
            'fields': ('is_converted', 'conversion_date', 'lost_reason'),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at', 'days_since_created', 
                      'days_since_last_contact'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = _('Full Name')
    full_name.admin_order_field = 'first_name'
    
    def days_since_created(self, obj):
        return obj.days_since_created
    days_since_created.short_description = _('Days Since Created')
    
    # Inline for activities
    class LeadActivityInline(admin.TabularInline):
        model = LeadActivity
        extra = 0
        fields = ('activity_type', 'subject', 'is_completed', 'completed_date', 'handled_by')
        readonly_fields = ('completed_date',)
        
        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "handled_by":
                # Limit to employee users only
                kwargs["queryset"] = Employee.objects.filter(user__is_staff=True)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    inlines = [LeadActivityInline]
    
    # Custom actions
    actions = ['mark_as_contacted', 'schedule_followup', 'convert_to_customer', 
               'mark_as_lost', 'export_leads_data']
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(
            status='contacted', 
            last_contact_date=timezone.now(),
            contact_attempts=models.F('contact_attempts') + 1
        )
        self.message_user(request, f"{updated} leads marked as contacted.")
    mark_as_contacted.short_description = _("Mark selected as contacted")
    
    def schedule_followup(self, request, queryset):
        # This would typically open a form to set followup date
        self.message_user(request, f"Schedule followup for {queryset.count()} leads")
    schedule_followup.short_description = _("Schedule followup for selected")
    
    def convert_to_customer(self, request, queryset):
        updated = queryset.update(
            status='converted',
            is_converted=True,
            conversion_date=timezone.now()
        )
        self.message_user(request, f"{updated} leads converted to customers.")
    convert_to_customer.short_description = _("Convert selected to customers")
    
    def mark_as_lost(self, request, queryset):
        # This would typically open a form to capture lost reason
        self.message_user(request, f"Mark {queryset.count()} leads as lost")
    mark_as_lost.short_description = _("Mark selected as lost")
    
    def export_leads_data(self, request, queryset):
        self.message_user(request, f"Preparing export for {queryset.count()} leads")
    export_leads_data.short_description = _("Export selected leads data")
    
    # Custom filters
    class OverdueFollowupFilter(admin.SimpleListFilter):
        title = _('overdue followup')
        parameter_name = 'overdue_followup'
        
        def lookups(self, request, model_admin):
            return (
                ('yes', _('Needs Followup')),
                ('no', _('Up to Date')),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'yes':
                return queryset.filter(
                    models.Q(next_followup_date__lt=timezone.now()) |
                    models.Q(next_followup_date__isnull=True, last_contact_date__lt=timezone.now() - timezone.timedelta(days=7))
                )
            return queryset
    
    list_filter = list_filter + (OverdueFollowupFilter,)
    
    # Auto-update last_contact_date when status changes
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'contacted':
            obj.last_contact_date = timezone.now()
            obj.contact_attempts += 1
        super().save_model(request, obj, form, change)


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ('lead_name', 'activity_type', 'subject', 'is_completed', 
                   'scheduled_date', 'handled_by', 'created_at')
    list_filter = ('activity_type', 'is_completed', 'scheduled_date', 'created_at')
    search_fields = ('lead__first_name', 'lead__last_name', 'lead__email', 
                    'subject', 'description')
    ordering = ('-scheduled_date', '-created_at')
    list_per_page = 25
    raw_id_fields = ('lead', 'handled_by')
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        (None, {
            'fields': ('lead', 'activity_type', 'subject', 'description')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_date', 'completed_date', 'is_completed')
        }),
        (_('Responsible Person'), {
            'fields': ('handled_by',)
        }),
    )
    
    # Custom methods for list display
    def lead_name(self, obj):
        return str(obj.lead.full_name)
    lead_name.short_description = _('Lead')
    lead_name.admin_order_field = 'lead__first_name'
    
    # Auto-set completed_date when marking as completed
    def save_model(self, request, obj, form, change):
        if obj.is_completed and not obj.completed_date:
            obj.completed_date = timezone.now()
        elif not obj.is_completed and obj.completed_date:
            obj.completed_date = None
        super().save_model(request, obj, form, change)
    
    # Custom action to mark activities as completed
    actions = ['mark_as_completed']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(
            is_completed=True,
            completed_date=timezone.now()
        )
        self.message_user(request, f"{updated} activities marked as completed.")
    mark_as_completed.short_description = _("Mark selected as completed")


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'total_leads', 'converted_leads', 
                   'conversion_rate', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-total_leads',)
    list_per_page = 20
    readonly_fields = ('total_leads', 'converted_leads', 'conversion_rate', 
                      'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Performance Metrics'), {
            'fields': ('total_leads', 'converted_leads', 'conversion_rate')
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def conversion_rate(self, obj):
        return f"{obj.conversion_rate}%"
    conversion_rate.short_description = _('Conversion Rate')
    
    # Custom action to reset statistics
    actions = ['reset_statistics']
    
    def reset_statistics(self, request, queryset):
        updated = queryset.update(total_leads=0, converted_leads=0)
        self.message_user(request, f"Statistics reset for {updated} lead sources.")
    reset_statistics.short_description = _("Reset statistics for selected")


