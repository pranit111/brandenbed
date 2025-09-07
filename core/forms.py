# forms.py
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from properties.models import Property
from leads.models import Lead


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5',
            'placeholder': 'Your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'shadow-sm bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5',
            'placeholder': 'name@example.com'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5',
            'placeholder': '+49 xxx xxxx xxxx'
        })
    )
    subject = forms.ChoiceField(
        choices=[
            ('', 'Choose a subject'),
            ('housing', 'Housing Inquiry'),
            ('landlord', 'Property Management'),
            ('support', 'Resident Support'),
            ('general', 'General Question'),
        ],
        widget=forms.Select(attrs={
            'class': 'bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block p-2.5 w-full text-sm text-gray-900 bg-white rounded-lg shadow-sm border border-gray-300 focus:ring-brand-gold focus:border-brand-gold',
            'placeholder': 'Tell us about your housing needs or questions...',
            'rows': 6
        })
    )

    def send_email(self):
        # Send email using the self.cleaned_data dictionary
        subject = f"{self.cleaned_data['subject']}: {self.cleaned_data['name']}"
        message = f"""
        From: {self.cleaned_data['name']} <{self.cleaned_data['email']}>
        Phone: {self.cleaned_data['phone'] or 'Not provided'}
        
        Message:
        {self.cleaned_data['message']}
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
# ================================
# SEARCH AND FILTER FORMS
# ================================

class PropertySearchForm(forms.Form):
    """Form for searching properties"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Search properties...'
        })
    )
    
    district = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'District'
        })
    )
    
    property_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Property.PROPERTY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    min_rent = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Min Rent',
            'step': '50'
        })
    )
    
    max_rent = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Max Rent',
            'step': '50'
        })
    )

class LeadSearchForm(forms.Form):
    """Form for searching and filtering leads"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Search leads...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Lead.LEAD_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    source = forms.ChoiceField(
        choices=[('', 'All Sources')] + Lead.LEAD_SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Lead.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )

# ================================
# QUICK ACTION FORMS
# ================================

class QuickNoteForm(forms.Form):
    """Quick note form for adding notes to various entities"""
    note = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'rows': 3,
            'placeholder': 'Add a quick note...'
        })
    )

class StatusUpdateForm(forms.Form):
    """Quick status update form"""
    status = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.choices = choices

# ================================
# BULK ACTION FORMS
# ================================

class BulkActionForm(forms.Form):
    """Form for bulk actions on multiple items"""
    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('delete', 'Delete Selected'),
        ('export', 'Export Selected'),
        ('assign', 'Assign to Staff'),
        ('update_status', 'Update Status'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    selected_items = forms.CharField(widget=forms.HiddenInput())

        
        
  