# properties/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from .models import Property, Room

class RoomInline(admin.TabularInline):
    """Inline for managing rooms within properties"""
    model = Room
    extra = 0
    fields = ('room_number', 'room_type', 'monthly_rent', 'status', 
             'max_occupants', 'current_occupants', 'is_available')
    readonly_fields = ('is_available',)
    show_change_link = True
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # This method is not needed for RoomInline as it doesn't have foreign keys
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_id', 'name', 'property_type', 'city', 'district', 
                   'status', 'total_rooms', 'total_beds', 'expected_monthly_rent', 
                   'created_at')
    list_filter = ('property_type', 'status', 'city', 'district', 'furnishing', 
                  'created_at', 'landlord')
    search_fields = ('property_id', 'name', 'address_line_1', 'city', 'district', 
                    'landlord__company_name', 'landlord__user__first_name', 
                    'landlord__user__last_name')
    ordering = ('-created_at',)
    list_per_page = 25
    raw_id_fields = ('landlord', 'property_manager', 'housekeeping_supervisor', 
                    'maintenance_supervisor')
    readonly_fields = ('total_capacity', 'occupied_beds', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    filter_horizontal = ()
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('property_id', 'name', 'property_type', 'furnishing')
        }),
        (_('Address Details'), {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 
                      'pincode', 'district')
        }),
        (_('Location Features'), {
            'fields': ('nearest_university', 'distance_to_university', 
                      'nearest_metro_station', 'distance_to_metro')
        }),
        (_('Property Specifications'), {
            'fields': ('total_rooms', 'total_beds', 'total_washrooms', 
                      'total_area', 'year_built')
        }),
        (_('Core BrandenBed Amenities'), {
            'fields': ('has_wifi', 'has_security', 'has_power_backup', 
                      'has_work_desk', 'has_shared_kitchen', 'has_shared_lounge'),
            'classes': ('collapse',)
        }),
        (_('Additional Amenities'), {
            'fields': ('has_laundry', 'has_gym', 'has_parking', 'has_balcony', 
                      'has_elevator', 'near_public_transport'),
            'classes': ('collapse',)
        }),
        (_('Management Team'), {
            'fields': ('property_manager', 'housekeeping_supervisor', 
                      'maintenance_supervisor'),
            'classes': ('collapse',)
        }),
        (_('Partnership Details'), {
            'fields': ('landlord', 'partnership_start_date', 'partnership_end_date')
        }),
        (_('Financial Information'), {
            'fields': ('expected_monthly_rent', 'security_deposit'),
            'classes': ('collapse',)
        }),
        (_('Availability & Status'), {
            'fields': ('available_from', 'status')
        }),
        (_('Additional Information'), {
            'fields': ('additional_notes', 'special_requirements'),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at', 'total_capacity', 'occupied_beds'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def total_rooms(self, obj):
        return obj.rooms.count()
    total_rooms.short_description = _('Total Rooms')
    
    def total_beds(self, obj):
        return sum(room.max_occupants for room in obj.rooms.all())
    total_beds.short_description = _('Total Beds')
    
    # Inline for rooms
    inlines = [RoomInline]
    
    # Custom actions
    actions = ['activate_properties', 'mark_under_maintenance', 'export_properties_data']
    
    def activate_properties(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} properties activated.")
    activate_properties.short_description = _("Activate selected properties")
    
    def mark_under_maintenance(self, request, queryset):
        updated = queryset.update(status='under_renovation')
        self.message_user(request, f"{updated} properties marked under maintenance.")
    mark_under_maintenance.short_description = _("Mark selected under maintenance")
    
    def export_properties_data(self, request, queryset):
        self.message_user(request, f"Preparing export for {queryset.count()} properties")
    export_properties_data.short_description = _("Export selected properties data")
    
    # Custom filters
    class AmenityFilter(admin.SimpleListFilter):
        title = _('amenities')
        parameter_name = 'amenities'
        
        def lookups(self, request, model_admin):
            return (
                ('wifi', _('Has WiFi')),
                ('security', _('Has Security')),
                ('laundry', _('Has Laundry')),
                ('gym', _('Has Gym')),
                ('parking', _('Has Parking')),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'wifi':
                return queryset.filter(has_wifi=True)
            elif self.value() == 'security':
                return queryset.filter(has_security=True)
            elif self.value() == 'laundry':
                return queryset.filter(has_laundry=True)
            elif self.value() == 'gym':
                return queryset.filter(has_gym=True)
            elif self.value() == 'parking':
                return queryset.filter(has_parking=True)
            return queryset
    
    list_filter = list_filter + (AmenityFilter,)
    
    # Prepopulate fields when adding
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['city'] = 'Berlin'
        initial['has_wifi'] = True
        initial['has_security'] = True
        initial['has_power_backup'] = True
        initial['has_work_desk'] = True
        initial['has_shared_kitchen'] = True
        initial['has_shared_lounge'] = True
        initial['near_public_transport'] = True
        return initial


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'property_ref', 'room_type', 'monthly_rent', 
                   'status', 'max_occupants', 'current_occupants', 'is_available', 
                   'available_from')
    list_filter = ('room_type', 'status', 'property_ref', 'has_private_bathroom', 
                  'utilities_included', 'created_at')
    search_fields = ('room_number', 'property_ref__name', 'property_ref__property_id', 
                    'description')
    ordering = ('property_ref', 'room_number')
    list_per_page = 25
    raw_id_fields = ('property_ref',)
    readonly_fields = ('is_available', 'created_at', 'updated_at')
    list_editable = ('status', 'current_occupants')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('property_ref', 'room_number', 'room_type')
        }),
        (_('Room Specifications'), {
            'fields': ('area', 'max_occupants', 'current_occupants')
        }),
        (_('Room Features'), {
            'fields': ('has_private_bathroom', 'has_work_desk', 'has_storage', 
                      'has_ac', 'has_window')
        }),
        (_('Pricing'), {
            'fields': ('monthly_rent', 'utilities_included', 'security_deposit')
        }),
        (_('Availability & Contract'), {
            'fields': ('status', 'available_from', 'min_contract_duration', 
                      'max_contract_duration')
        }),
        (_('Additional Information'), {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at', 'is_available'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for list display
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = _('Available')
    
    # Custom actions
    actions = ['mark_available', 'mark_occupied', 'mark_maintenance', 'export_rooms_data']
    
    def mark_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f"{updated} rooms marked as available.")
    mark_available.short_description = _("Mark selected as available")
    
    def mark_occupied(self, request, queryset):
        updated = queryset.update(status='occupied')
        self.message_user(request, f"{updated} rooms marked as occupied.")
    mark_occupied.short_description = _("Mark selected as occupied")
    
    def mark_maintenance(self, request, queryset):
        updated = queryset.update(status='maintenance')
        self.message_user(request, f"{updated} rooms marked under maintenance.")
    mark_maintenance.short_description = _("Mark selected under maintenance")
    
    def export_rooms_data(self, request, queryset):
        self.message_user(request, f"Preparing export for {queryset.count()} rooms")
    export_rooms_data.short_description = _("Export selected rooms data")
    
    # Auto-update property room counts when room is saved
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update property room counts (this would be better handled by signals)
        obj.property_ref.save()
    
    # Filter rooms by property in the admin
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add any custom filtering logic here
        return qs

