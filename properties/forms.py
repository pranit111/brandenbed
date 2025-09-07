from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

# Import all models
from accounts.models import User
from employees.models import Employee, Role
from properties.models import Property, Room
from landlords.models import Landlord, LandlordDocument
from residents.models import Resident, ResidencyContract
from leads.models import Lead, LeadActivity
from payments.models import Payment, PaymentType, PaymentReminder
from support.models import SupportTicket, SupportCategory, TicketComment
from maintenance.models import MaintenanceRequest, Vendor
from housekeeping.models import HousekeepingSchedule

# ================================
# PROPERTY FORMS
# ================================

class PropertyForm(forms.ModelForm):
    """Form for adding/editing properties"""
    
    class Meta:
        model = Property
        exclude = ['property_id', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Property Name'
            }),
            'property_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'furnishing': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Street Address'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Apartment, suite, etc. (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': '10115'
            }),
            'district': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Mitte, Kreuzberg, etc.'
            }),
            'nearest_university': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Humboldt University'
            }),
            'distance_to_university': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': '10 mins walk'
            }),
            'total_rooms': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'total_beds': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'total_washrooms': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'total_area': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'expected_monthly_rent': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01'
            }),
            'security_deposit': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01'
            }),
            'partnership_start_date': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add boolean field styling for checkboxes
        boolean_fields = [
            'has_wifi', 'has_security', 'has_power_backup', 'has_work_desk',
            'has_shared_kitchen', 'has_shared_lounge', 'has_laundry', 'has_gym',
            'has_parking', 'has_balcony', 'has_elevator', 'near_public_transport'
        ]
        for field_name in boolean_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
                })








class RoomForm(forms.ModelForm):
    """Form for adding/editing rooms"""
    
    class Meta:
        model = Room
        fields = [
            'room_number', 'room_type', 'area', 'max_occupants', 'current_occupants',
            'monthly_rent', 'security_deposit', 'available_from', 'status',
            'min_contract_duration', 'max_contract_duration', 'utilities_included',
            'has_private_bathroom', 'has_work_desk', 'has_storage', 'has_ac', 'has_window',
            'description'
        ]
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': '101, A1, etc.',
                'maxlength': '10'
            }),
            'room_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01',
                'min': '5.00',
                'max': '200.00'
            }),
            'max_occupants': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'min': '1',
                'max': '4'
            }),
            'current_occupants': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'min': '0'
            }),
            'monthly_rent': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01',
                'min': '50.00'
            }),
            'security_deposit': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01',
                'min': '0.00'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'min_contract_duration': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'min': '1',
                'max': '36'
            }),
            'max_contract_duration': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'min': '1',
                'max': '36'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 4,
                'placeholder': 'Describe the room features, layout, and any special characteristics...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract property_obj from kwargs
        self.property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)
        
        # Set default values for new rooms
        if not self.instance.pk:
            self.fields['available_from'].initial = date.today()
            self.fields['current_occupants'].initial = 0
            # Hide current_occupants field for new rooms
            self.fields['current_occupants'].widget = forms.HiddenInput()
        
        # Add boolean field styling for checkboxes
        boolean_fields = [
            'has_private_bathroom', 'has_work_desk', 'has_storage', 
            'has_ac', 'has_window', 'utilities_included'
        ]
        
        for field_name in boolean_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
                })
        
        # Mark required fields
        required_fields = [
            'room_number', 'room_type', 'area', 'max_occupants', 
            'monthly_rent', 'security_deposit', 'available_from', 
            'min_contract_duration', 'max_contract_duration'
        ]
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_room_number(self):
        """Validate room number uniqueness within property"""
        room_number = self.cleaned_data.get('room_number')
        if not room_number:
            raise forms.ValidationError("Room number is required.")
        
        # Remove extra whitespace and convert to uppercase for consistency
        room_number = room_number.strip().upper()
        
        # Check for uniqueness within the property - only if we have property context
        if self.property_obj:
            existing_room = Room.objects.filter(
                property_ref=self.property_obj,
                room_number=room_number
            )
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_room = existing_room.exclude(pk=self.instance.pk)
            
            if existing_room.exists():
                raise forms.ValidationError(
                    f"Room number '{room_number}' already exists in this property."
                )
        
        return room_number
    
    def clean_available_from(self):
        """Validate available_from date"""
        available_from = self.cleaned_data.get('available_from')
        if available_from:
            # For new rooms, don't allow past dates
            if not self.instance.pk and available_from < date.today():
                raise forms.ValidationError("Available from date cannot be in the past.")
        return available_from
    
    def clean_area(self):
        """Validate room area"""
        area = self.cleaned_data.get('area')
        if area:
            if area < Decimal('5.0'):
                raise forms.ValidationError("Room area must be at least 5 m².")
            if area > Decimal('200.0'):
                raise forms.ValidationError("Room area cannot exceed 200 m². Please verify the measurement.")
        return area
    
    def clean_monthly_rent(self):
        """Validate monthly rent"""
        monthly_rent = self.cleaned_data.get('monthly_rent')
        if monthly_rent:
            if monthly_rent < Decimal('50.0'):
                raise forms.ValidationError("Monthly rent must be at least €50.")
            if monthly_rent > Decimal('5000.0'):
                raise forms.ValidationError("Monthly rent seems unusually high. Please verify the amount.")
        return monthly_rent
    
    def clean_security_deposit(self):
        """Validate security deposit"""
        security_deposit = self.cleaned_data.get('security_deposit')
        monthly_rent = self.cleaned_data.get('monthly_rent')
        
        if security_deposit is not None:
            if security_deposit < Decimal('0.0'):
                raise forms.ValidationError("Security deposit cannot be negative.")
            
            # Warn if deposit is unusually high compared to rent
            if monthly_rent and security_deposit > (monthly_rent * 3):
                raise forms.ValidationError(
                    "Security deposit seems unusually high compared to monthly rent. "
                    "Typically, it should be 1-3 times the monthly rent."
                )
        
        return security_deposit
    
    def clean(self):
        """Custom validation for cross-field dependencies"""
        cleaned_data = super().clean()
        
        # Validate contract durations
        min_duration = cleaned_data.get('min_contract_duration')
        max_duration = cleaned_data.get('max_contract_duration')
        
        if min_duration and max_duration and min_duration > max_duration:
            raise forms.ValidationError({
                'max_contract_duration': 'Maximum contract duration must be greater than or equal to minimum duration.'
            })
        
        # Validate occupancy
        current_occupants = cleaned_data.get('current_occupants', 0)
        max_occupants = cleaned_data.get('max_occupants')
        
        if current_occupants and max_occupants and current_occupants > max_occupants:
            raise forms.ValidationError({
                'current_occupants': 'Current occupants cannot exceed maximum occupants.'
            })
        
        # Additional business logic validations
        room_type = cleaned_data.get('room_type')
        max_occupants = cleaned_data.get('max_occupants')
        
        # Validate occupancy based on room type
        if room_type == 'single' and max_occupants and max_occupants > 1:
            raise forms.ValidationError({
                'max_occupants': 'Single occupancy rooms can only have 1 occupant.'
            })
        elif room_type == 'double' and max_occupants and max_occupants > 2:
            raise forms.ValidationError({
                'max_occupants': 'Double occupancy rooms can have at most 2 occupants.'
            })
        
        return cleaned_data














