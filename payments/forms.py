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
# PAYMENT FORMS
# ================================

class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
    class Meta:
        model = Payment
        exclude = ['payment_id', 'created_at', 'updated_at', 'recorded_by', 'verified_by']
        widgets = {
            'resident': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'landlord': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'property': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'room': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'direction': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Bank transaction reference'
            }),
            'transaction_date': forms.DateTimeInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'payment_period_start': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'payment_period_end': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'receipt_file': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3
            })
        }
