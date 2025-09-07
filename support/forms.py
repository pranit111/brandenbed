# support/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import SupportTicket, SupportCategory, TicketComment
from residents.models import Resident
from employees.models import Employee
from properties.models import Property, Room

class SupportTicketForm(forms.ModelForm):
    """Form for creating support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = [
            'resident', 'property_ref', 'room', 'category', 
            'subject', 'description', 'priority', 'assigned_to',
            'estimated_cost', 'requires_followup', 'followup_date'
        ]
        widgets = {
            'resident': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select resident...'
            }),
            'property_ref': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select property...'
            }),
            'room': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select room (optional)...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue...',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the issue, location, and any relevant information...'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Auto-assign or select employee...'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'followup_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize querysets
        self.fields['resident'].queryset = Resident.objects.select_related('user').order_by('user__first_name', 'user__last_name')
        self.fields['property_ref'].queryset = Property.objects.filter(status='active').order_by('name')
        # self.fields['assigned_to'].queryset = Employee.objects.filter(
        #     user__is_active=True,
        #     department__in=['maintenance', 'customer_service', 'management']
        # ).select_related('user').order_by('user__first_name', 'user__last_name')
        
        # Make assigned_to optional
        self.fields['assigned_to'].required = False
        self.fields['room'].required = False
        self.fields['estimated_cost'].required = False
        self.fields['followup_date'].required = False
        
        # Set priority based on category if selected
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                category = SupportCategory.objects.get(id=category_id)
                self.fields['priority'].initial = category.priority_level
            except (ValueError, SupportCategory.DoesNotExist):
                pass
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 5:
            raise ValidationError("Subject must be at least 5 characters long.")
        return subject
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise ValidationError("Description must be at least 10 characters long.")
        return description
    
    def clean_followup_date(self):
        followup_date = self.cleaned_data.get('followup_date')
        requires_followup = self.cleaned_data.get('requires_followup')
        
        if requires_followup and not followup_date:
            raise ValidationError("Follow-up date is required when follow-up is needed.")
        
        if followup_date and followup_date <= timezone.now().date():
            raise ValidationError("Follow-up date must be in the future.")
        
        return followup_date
    
    def clean(self):
        cleaned_data = super().clean()
        property_ref = cleaned_data.get('property_ref')
        room = cleaned_data.get('room')
        
        # Validate room belongs to selected property
        if room and property_ref and room.property_ref != property_ref:
            raise ValidationError("Selected room does not belong to the selected property.")
        
        return cleaned_data

class TicketUpdateForm(forms.ModelForm):
    """Form for updating ticket status, assignment, etc."""
    
    class Meta:
        model = SupportTicket
        fields = [
            'status', 'priority', 'assigned_to', 'estimated_cost', 
            'actual_cost', 'requires_followup', 'followup_date'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select employee...'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'actual_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'followup_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['assigned_to'].queryset = Employee.objects.filter(
            user__is_active=True
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        
        # Make fields optional
        for field_name in ['assigned_to', 'estimated_cost', 'actual_cost', 'followup_date']:
            self.fields[field_name].required = False

class TicketCommentForm(forms.ModelForm):
    """Form for adding comments to tickets"""
    
    class Meta:
        model = TicketComment
        fields = ['comment_type', 'comment', 'is_internal', 'attachment']
        widgets = {
            'comment_type': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add your comment or update...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachment'].required = False
        
        # Set default comment type
        self.fields['comment_type'].initial = 'internal'
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment.strip()) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        return comment.strip()
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (max 5MB)
            if attachment.size > 5 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 5MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt']
            file_extension = attachment.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError("File type not supported. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT")
        
        return attachment

class TicketFilterForm(forms.Form):
    """Form for filtering tickets in list view"""
    
    STATUS_CHOICES = [('', 'All Statuses')] + SupportTicket.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'All Priorities')] + SupportTicket.PRIORITY_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by ticket ID, subject, or resident name...'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=SupportCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=Employee.objects.filter(user__is_active=True).select_related('user'),
        required=False,
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("Start date cannot be after end date.")
        
        return cleaned_data

class SupportCategoryForm(forms.ModelForm):
    """Form for creating and updating support categories"""
    
    class Meta:
        model = SupportCategory
        fields = ['name', 'description', 'priority_level', 'sla_hours']
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Describe this category and what types of issues it covers...'
            }),
            'priority_level': forms.Select(
                choices=[(1, 'High Priority'), (2, 'Medium Priority'), (3, 'Low Priority')],
                attrs={
                    'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                }
            ),
            'sla_hours': forms.NumberInput(attrs={
                'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': 1,
                'max': 168,  # 1 week max
                'placeholder': 'Enter hours (e.g., 24 for 1 day)'
            })
        }
        help_texts = {
            'priority_level': 'Default priority level for tickets in this category (1=High, 2=Medium, 3=Low)',
            'sla_hours': 'Service Level Agreement - target response time in hours',
        }

    def clean_sla_hours(self):
        """Validate SLA hours"""
        sla_hours = self.cleaned_data.get('sla_hours')
        if sla_hours and (sla_hours < 1 or sla_hours > 168):
            raise forms.ValidationError('SLA hours must be between 1 and 168 (1 week)')
        return sla_hours


class CategoryFilterForm(forms.Form):
    """Form for filtering support categories"""
    
    PRIORITY_CHOICES = [
        ('', 'All Priorities'),
        ('1', 'High Priority'),
        ('2', 'Medium Priority'),
        ('3', 'Low Priority'),
    ]
    
    priority_level = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Search categories...'
        })
    )

class BulkTicketActionForm(forms.Form):
    """Form for bulk actions on tickets"""
    
    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('assign', 'Assign to Employee'),
        ('update_priority', 'Update Priority'),
        ('update_status', 'Update Status'),
        ('add_category', 'Change Category')
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=Employee.objects.filter(user__is_active=True).select_related('user'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'Select Priority')] + SupportTicket.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Select Status')] + SupportTicket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=SupportCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        
        if action == 'assign' and not cleaned_data.get('assigned_to'):
            raise ValidationError("Please select an employee to assign tickets to.")
        elif action == 'update_priority' and not cleaned_data.get('priority'):
            raise ValidationError("Please select a priority level.")
        elif action == 'update_status' and not cleaned_data.get('status'):
            raise ValidationError("Please select a status.")
        elif action == 'add_category' and not cleaned_data.get('category'):
            raise ValidationError("Please select a category.")
        
        return cleaned_data