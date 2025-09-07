
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
# HOUSEKEEPING FORMS
# ================================

class HousekeepingScheduleForm(forms.ModelForm):
    """Form for scheduling housekeeping"""
    
    class Meta:
        model = HousekeepingSchedule
        exclude = ['schedule_id', 'created_at', 'updated_at', 'started_time', 'completed_time', 'quality_checked_by']
        widgets = {
            'property': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'room': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'schedule_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'datetime-local'
            }),
            'estimated_duration': forms.TimeInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'time'
            }),
            'assigned_staff': forms.SelectMultiple(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'supervisor': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'completion_notes': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3
            }),
            'issues_found': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3
            })
        }
