# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Configuration for list view
    list_display = ('username', 'email', 'get_full_name', 'user_type', 
                   'city', 'country', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'country', 
                  'city', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 
                    'phone_number', 'city')
    ordering = ('-date_joined',)
    list_per_page = 25
    
    # Fieldsets for detail view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 
                                       'date_of_birth', 'profile_picture')}),
        (_('User Type'), {'fields': ('user_type',)}),
        (_('Contact info'), {'fields': ('phone_number', 'whatsapp_number')}),
        (_('Address'), {'fields': ('address_line_1', 'address_line_2', 
                                 'city', 'state', 'pincode', 'country')}),
        (_('Personal Details'), {'fields': ('nationality', 'preferred_language')}),
        (_('Emergency Contact'), {'fields': ('emergency_contact_name', 
                                           'emergency_contact_phone', 
                                           'emergency_contact_relation')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Communication Preferences'), {'fields': ('marketing_consent', 
                                                   'whatsapp_consent')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fieldsets for add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
        (_('Personal info'), {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
    )
    
    # Custom methods for list display
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')
    
    # Filtering by user type in the admin
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add any custom filtering logic here if needed
        return qs
    
    # Action to export selected users
    actions = ['export_selected_users']
    
    def export_selected_users(self, request, queryset):
        # This would typically export user data - implementation depends on your needs
        # For example, you could use django-import-export or generate a CSV
        self.message_user(request, f"Preparing export for {queryset.count()} users")
    export_selected_users.short_description = _("Export selected users")
    
    # Readonly fields for non-editable information
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('last_login', 'date_joined')
        return ()
    
    # Custom filters for different user types
    class UserTypeFilter(admin.SimpleListFilter):
        title = _('user type')
        parameter_name = 'user_type'
        
        def lookups(self, request, model_admin):
            return User.USER_TYPE_CHOICES
        
        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(user_type=self.value())
            return queryset

