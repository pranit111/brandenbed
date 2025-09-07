# residents/admin.py
from datetime import timezone
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django import forms

from . import models
from .models import Resident, ResidencyContract

class ResidencyContractInline(admin.TabularInline):
    """Inline for managing contracts within residents"""
    model = ResidencyContract
    extra = 0
    fields = ('contract_id', 'property_ref', 'room', 'start_date', 'end_date', 
             'monthly_rent', 'status', 'is_active')
    readonly_fields = ('is_active',)
    show_change_link = True
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # This method is not needed for ResidencyContractInline as it doesn't have foreign keys
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('resident_id', 'user_full_name', 'resident_type', 'status', 
                   'current_property', 'verification_status', 'move_in_date', 
                   'created_at')
    list_filter = ('resident_type', 'status', 'current_property', 'verification_completed',
                  'deposit_paid', 'agreement_signed', 'created_at')
    search_fields = ('resident_id', 'user__first_name', 'user__last_name', 
                    'user__email', 'university', 'employer', 'identification_number')
    ordering = ('-created_at',)
    list_per_page = 25
    raw_id_fields = ('user', 'current_property', 'current_room', 'assigned_support_agent')
    readonly_fields = ('is_international', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'resident_id', 'resident_type', 'status')
        }),
        (_('Identification'), {
            'fields': ('identification_type', 'identification_number')
        }),
        (_('Academic Information'), {
            'fields': ('university', 'course', 'enrollment_proof'),
            'classes': ('collapse',)
        }),
        (_('Professional Information'), {
            'fields': ('employer', 'job_title', 'employment_proof'),
            'classes': ('collapse',)
        }),
        (_('Financial Information'), {
            'fields': ('monthly_income', 'income_source'),
            'classes': ('collapse',)
        }),
        (_('Visa & Legal Status (International)'), {
            'fields': ('visa_type', 'visa_expiry'),
            'classes': ('collapse',)
        }),
        (_('Residency Details'), {
            'fields': ('current_property', 'current_room', 'move_in_date', 'move_out_date')
        }),
        (_('Support & Management'), {
            'fields': ('assigned_support_agent',)
        }),
        (_('Emergency Contact'), {
            'fields': ('parent_guardian_name', 'parent_guardian_phone', 'parent_guardian_email'),
            'classes': ('collapse',)
        }),
        (_('Special Requirements'), {
            'fields': ('dietary_requirements', 'medical_conditions', 'special_needs'),
            'classes': ('collapse',)
        }),
        (_('Onboarding Progress'), {
            'fields': ('verification_completed', 'deposit_paid', 'agreement_signed', 
                      'orientation_completed')
        }),
        (_('Preferences'), {
            'fields': ('preferred_room_type', 'preferred_location', 'budget_range'),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at', 'is_international'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def user_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else "No User"
    user_full_name.short_description = _('Resident Name')
    user_full_name.admin_order_field = 'user__first_name'
    
    def verification_status(self, obj):
        if obj.verification_completed:
            return _("Verified")
        return _("Pending")
    verification_status.short_description = _('Verification')
    verification_status.admin_order_field = 'verification_completed'
    
    # Inline for contracts
    inlines = [ResidencyContractInline]
    
    # Custom actions
    actions = ['mark_verified', 'mark_active', 'mark_moved_out', 'export_residents_data']
    
    def mark_verified(self, request, queryset):
        updated = queryset.update(verification_completed=True)
        self.message_user(request, f"{updated} residents marked as verified.")
    mark_verified.short_description = _("Mark selected as verified")
    
    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} residents marked as active.")
    mark_active.short_description = _("Mark selected as active")
    
    def mark_moved_out(self, request, queryset):
        updated = queryset.update(status='moved_out', move_out_date=timezone.now().date())
        self.message_user(request, f"{updated} residents marked as moved out.")
    mark_moved_out.short_description = _("Mark selected as moved out")
    
    def export_residents_data(self, request, queryset):
        self.message_user(request, f"Preparing export for {queryset.count()} residents")
    export_residents_data.short_description = _("Export selected residents data")
    
    # Custom filters
    class OnboardingStatusFilter(admin.SimpleListFilter):
        title = _('onboarding status')
        parameter_name = 'onboarding_status'
        
        def lookups(self, request, model_admin):
            return (
                ('complete', _('Onboarding Complete')),
                ('incomplete', _('Onboarding Incomplete')),
                ('deposit_pending', _('Deposit Pending')),
                ('agreement_pending', _('Agreement Pending')),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'complete':
                return queryset.filter(
                    verification_completed=True,
                    deposit_paid=True,
                    agreement_signed=True,
                    orientation_completed=True
                )
            elif self.value() == 'incomplete':
                return queryset.filter(
                    models.Q(verification_completed=False) |
                    models.Q(deposit_paid=False) |
                    models.Q(agreement_signed=False) |
                    models.Q(orientation_completed=False)
                )
            elif self.value() == 'deposit_pending':
                return queryset.filter(deposit_paid=False)
            elif self.value() == 'agreement_pending':
                return queryset.filter(agreement_signed=False)
            return queryset
    
    list_filter = list_filter + (OnboardingStatusFilter,)
    
    # Prepopulate fields when adding
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['status'] = 'lead'
        return initial


@admin.register(ResidencyContract)
class ResidencyContractAdmin(admin.ModelAdmin):
    list_display = ('contract_id', 'resident_name', 'property_ref', 'room', 
                   'start_date', 'end_date', 'monthly_rent', 'status', 
                   'is_active', 'days_remaining')
    list_filter = ('status', 'property_ref', 'utilities_included', 'start_date', 
                  'end_date', 'created_at')
    search_fields = ('contract_id', 'resident__user__first_name', 
                    'resident__user__last_name', 'property_ref__name', 
                    'room__room_number')
    ordering = ('-created_at',)
    list_per_page = 25
    raw_id_fields = ('resident', 'property_ref', 'room', 'created_by')
    readonly_fields = ('is_active', 'days_remaining', 'created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (_('Contract Identification'), {
            'fields': ('contract_id', 'resident', 'property_ref', 'room')
        }),
        (_('Contract Terms'), {
            'fields': ('start_date', 'end_date', 'monthly_rent', 'security_deposit')
        }),
        (_('Fees'), {
            'fields': ('admin_fee', 'cleaning_fee'),
            'classes': ('collapse',)
        }),
        (_('Contract Details'), {
            'fields': ('notice_period_days', 'utilities_included')
        }),
        (_('Status and Signing'), {
            'fields': ('status', 'signed_date', 'contract_file')
        }),
        (_('Contract Content'), {
            'fields': ('terms_and_conditions', 'special_clauses'),
            'classes': ('collapse',)
        }),
        (_('Management'), {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at', 'is_active', 'days_remaining'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def resident_name(self, obj):
        return str(obj.resident)
    resident_name.short_description = _('Resident')
    resident_name.admin_order_field = 'resident__user__first_name'
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = _('Active')
    
    def days_remaining(self, obj):
        return obj.days_remaining
    days_remaining.short_description = _('Days Remaining')
    
    # Custom actions
    actions = ['mark_active', 'mark_signed', 'mark_expired', 'export_contracts_data']
    
    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} contracts marked as active.")
    mark_active.short_description = _("Mark selected as active")
    
    def mark_signed(self, request, queryset):
        updated = queryset.update(
            status='signed' if not obj.is_active else 'active',
            signed_date=timezone.now()
        )
        self.message_user(request, f"{updated} contracts marked as signed.")
    mark_signed.short_description = _("Mark selected as signed")
    
    def mark_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f"{updated} contracts marked as expired.")
    mark_expired.short_description = _("Mark selected as expired")
    
    def export_contracts_data(self, request, queryset):
        self.message_user(request, f"Preparing export for {queryset.count()} contracts")
    export_contracts_data.short_description = _("Export selected contracts data")
    
    # Auto-set created_by to current user
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only on create
            obj.created_by = request.user.employee if hasattr(request.user, 'employee') else None
        super().save_model(request, obj, form, change)
    
    # Filter for active contracts by default
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show active contracts by default
        if not request.GET.get('status'):
            qs = qs.filter(status='active')
        return qs

