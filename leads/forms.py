# leads/forms.py
from django import forms
from .models import Lead, LeadActivity

class ContactUsForm(forms.ModelForm):
    """Form for general contact inquiries"""
    
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'subject', 'message', 'preferred_location', 'budget_range', 'move_in_date'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'your@email.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+49 123 456 789'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'What can we help you with?'
            }),
            'message': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Tell us about your housing needs...'
            }),
            'preferred_location': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., Mitte, Kreuzberg, Charlottenburg'
            }),
            'budget_range': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., 400-600 EUR'
            }),
            'move_in_date': forms.DateInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
        }
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        lead.lead_type = 'tenant'
        lead.source = 'website_contact'
        if commit:
            lead.save()
        return lead


class LandlordPartnershipForm(forms.ModelForm):
    """Form for landlord partnership inquiries"""
    
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'company_name', 'property_address', 'property_type',
            'number_of_rooms', 'monthly_rent_expectation', 'property_description'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'your@email.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+49 123 456 789'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Your company name (optional)'
            }),
            'property_address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Complete property address including postal code'
            }),
            'property_type': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'number_of_rooms': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Total number of rooms'
            }),
            'monthly_rent_expectation': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., 1200 EUR per month'
            }),
            'property_description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Describe your property, amenities, and what makes it special...'
            }),
        }
    
    def save(self, commit=True):
        lead = super().save(commit=False)
        lead.lead_type = 'landlord'
        lead.source = 'website_landlord'
        lead.subject = f'Landlord Partnership - {lead.property_type or "Property"} in Berlin'
        lead.message = f'New landlord partnership inquiry for {lead.property_type or "property"} at {lead.property_address}'
        if commit:
            lead.save()
        return lead


class LeadManagementForm(forms.ModelForm):
    """Form for managing leads in the admin interface"""
    
    class Meta:
        model = Lead
        fields = [
            'status', 'priority', 'assigned_to', 'next_followup_date',
            'notes', 'lost_reason'
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'priority': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'next_followup_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Add notes about this lead...'
            }),
            'lost_reason': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Reason for losing this lead'
            }),
        }


class LeadActivityForm(forms.ModelForm):
    """Form for adding activities to leads"""
    
    class Meta:
        model = LeadActivity
        fields = [
            'activity_type', 'subject', 'description', 'scheduled_date', 'is_completed'
        ]
        widgets = {
            'activity_type': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Activity subject'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Activity details...'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'type': 'datetime-local'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
        }


class LeadFilterForm(forms.Form):
    """Form for filtering leads in the list view"""
    
    STATUS_CHOICES = [('', 'All Statuses')] + Lead.LEAD_STATUS_CHOICES
    TYPE_CHOICES = [('', 'All Types')] + Lead.LEAD_TYPE_CHOICES
    PRIORITY_CHOICES = [('', 'All Priorities')] + Lead.PRIORITY_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    lead_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-l-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Search by name, email...'
        })
    )