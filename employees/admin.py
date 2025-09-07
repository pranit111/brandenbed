# employees/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Role, Employee

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'get_permission_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        (_('Property Management Permissions'), {
            'fields': ('can_manage_properties', 'can_manage_landlords', 'can_manage_residents')
        }),
        (_('Operational Permissions'), {
            'fields': ('can_handle_payments', 'can_manage_employees', 'can_view_reports')
        }),
        (_('Service Permissions'), {
            'fields': ('can_handle_maintenance', 'can_handle_support_tickets', 
                      'can_manage_housekeeping')
        }),
        (_('Business Development Permissions'), {
            'fields': ('can_manage_leads', 'can_access_crm')
        }),
    )
    
    def description_preview(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_preview.short_description = _('Description Preview')
    
    def get_permission_count(self, obj):
        # Count the number of True permission fields
        permission_fields = [f for f in obj._meta.fields 
                           if f.name.startswith('can_') and isinstance(f, models.BooleanField)]
        true_count = sum(1 for field in permission_fields if getattr(obj, field.name))
        return f"{true_count}/{len(permission_fields)}"
    get_permission_count.short_description = _('Active Permissions')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user_full_name', 'role', 'employment_status', 
                   'employment_type', 'hire_date', 'work_location')
    list_filter = ('employment_status', 'employment_type', 'role', 'hire_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 
                    'user__email', 'work_location')
    ordering = ('-hire_date',)
    list_per_page = 25
    raw_id_fields = ('user', 'manager')  # Better for performance with many users
    autocomplete_fields = ['role']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'employee_id', 'role')
        }),
        (_('Employment Details'), {
            'fields': ('employment_type', 'employment_status', 'manager',
                      'hire_date', 'probation_end_date', 'termination_date')
        }),
        (_('Compensation'), {
            'fields': ('monthly_salary',),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
        (_('Work Details'), {
            'fields': ('work_location', 'shift_timing')
        }),
        (_('Skills & Qualifications'), {
            'fields': ('skills', 'certifications'),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else "No User"
    user_full_name.short_description = _('Employee Name')
    user_full_name.admin_order_field = 'user__first_name'
    
    # Inline for employees managed by this employee (if they are a manager)
    class ManagedEmployeesInline(admin.TabularInline):
        model = Employee
        fk_name = 'manager'
        extra = 0
        can_delete = False
        fields = ('employee_id', 'user_full_name', 'role', 'employment_status')
        readonly_fields = ('employee_id', 'user_full_name', 'role', 'employment_status')
        
        def user_full_name(self, obj):
            return obj.user.get_full_name()
        user_full_name.short_description = _('Employee Name')
    
    def get_inlines(self, request, obj):
        if obj and obj.is_manager:
            return [self.ManagedEmployeesInline]
        return []
    
    # Custom actions
    actions = ['mark_as_active', 'mark_as_inactive', 'export_employee_data']
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(employment_status='active')
        self.message_user(request, f"{updated} employees marked as active.")
    mark_as_active.short_description = _("Mark selected employees as active")
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(employment_status='inactive')
        self.message_user(request, f"{updated} employees marked as inactive.")
    mark_as_inactive.short_description = _("Mark selected employees as inactive")
    
    def export_employee_data(self, request, queryset):
        # Placeholder for export functionality
        # Could be implemented with django-import-export or custom CSV generation
        self.message_user(request, f"Preparing export for {queryset.count()} employees")
    export_employee_data.short_description = _("Export selected employees data")
    
    # Readonly fields based on object state
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('employee_id',)  # Employee ID shouldn't be changed after creation
        return ()
    
    # Filter for active employees only by default
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show all employees to superusers, only active to others
        if not request.user.is_superuser:
            qs = qs.filter(employment_status='active')
        return qs
    
    # Prepopulate fields when adding
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['employment_status'] = 'active'
        initial['employment_type'] = 'full_time'
        return initial
