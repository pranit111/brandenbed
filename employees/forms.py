# employees/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Employee, Role

User = get_user_model()

class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees"""
    
    # User fields
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Enter first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Enter last name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Enter email address'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Enter username'
        })
    )
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Enter password'
        }),
        help_text='Leave blank to keep current password when editing'
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': '+91 9876543210'
        })
    )
    
    whatsapp_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': '+91 9876543210'
        })
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'type': 'date'
        })
    )
    
    address_line_1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Street address, building name'
        })
    )
    
    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Apartment, floor, area (optional)'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'City'
        })
    )
    
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'State'
        })
    )
    
    pincode = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': '400001'
        })
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'role', 'employment_type', 'employment_status',
            'manager', 'hire_date', 'probation_end_date', 'monthly_salary',
            'work_location', 'shift_timing', 'skills', 'certifications', 'notes'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'EMP001'
            }),
            'role': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'manager': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'probation_end_date': forms.DateInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'type': 'date'
            }),
            'monthly_salary': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': '50000'
            }),
            'work_location': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': 'Main Office / Property Name'
            }),
            'shift_timing': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'placeholder': '9:00 AM - 6:00 PM'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3,
                'placeholder': 'e.g., Property Management, Customer Service, Maintenance'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3,
                'placeholder': 'List any relevant certifications'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 4,
                'placeholder': 'Additional notes about the employee'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing employee, populate user fields
        if self.instance and self.instance.pk and self.instance.user:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            self.fields['phone_number'].initial = getattr(user, 'phone_number', '')
            self.fields['whatsapp_number'].initial = getattr(user, 'whatsapp_number', '')
            self.fields['date_of_birth'].initial = getattr(user, 'date_of_birth', None)
            self.fields['address_line_1'].initial = getattr(user, 'address_line_1', '')
            self.fields['address_line_2'].initial = getattr(user, 'address_line_2', '')
            self.fields['city'].initial = getattr(user, 'city', '')
            self.fields['state'].initial = getattr(user, 'state', '')
            self.fields['pincode'].initial = getattr(user, 'pincode', '')
            
            # Make password not required for editing
            self.fields['password'].required = False
        else:
            # Password required for new employees
            self.fields['password'].required = True
        
        # Filter manager choices to exclude self and inactive employees
        if self.instance and self.instance.pk:
            self.fields['manager'].queryset = Employee.objects.filter(
                employment_status='active'
            ).exclude(pk=self.instance.pk).select_related('user')
        else:
            self.fields['manager'].queryset = Employee.objects.filter(
                employment_status='active'
            ).select_related('user')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current user if editing)
            existing_user = User.objects.filter(email=email)
            if self.instance and self.instance.pk and self.instance.user:
                existing_user = existing_user.exclude(pk=self.instance.user.pk)
            
            if existing_user.exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username already exists (excluding current user if editing)
            existing_user = User.objects.filter(username=username)
            if self.instance and self.instance.pk and self.instance.user:
                existing_user = existing_user.exclude(pk=self.instance.user.pk)
            
            if existing_user.exists():
                raise ValidationError("A user with this username already exists.")
        return username

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            # Check if employee ID already exists (excluding current employee if editing)
            existing_employee = Employee.objects.filter(employee_id=employee_id)
            if self.instance and self.instance.pk:
                existing_employee = existing_employee.exclude(pk=self.instance.pk)
            
            if existing_employee.exists():
                raise ValidationError("An employee with this ID already exists.")
        return employee_id

    def save(self, commit=True):
        # Get or create user
        if self.instance.pk and self.instance.user:
            # Editing existing employee
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.username = self.cleaned_data['username']
            
            # Update password only if provided
            password = self.cleaned_data.get('password')
            if password:
                user.set_password(password)
        else:
            # Creating new employee
            user = User(
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                username=self.cleaned_data['username'],
            )
            user.set_password(self.cleaned_data['password'])
        
        # Update additional user fields
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.whatsapp_number = self.cleaned_data.get('whatsapp_number', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.address_line_1 = self.cleaned_data.get('address_line_1', '')
        user.address_line_2 = self.cleaned_data.get('address_line_2', '')
        user.city = self.cleaned_data.get('city', '')
        user.state = self.cleaned_data.get('state', '')
        user.pincode = self.cleaned_data.get('pincode', '')
        
        if commit:
            user.save()
        
        # Save employee
        employee = super().save(commit=False)
        employee.user = user
        
        if commit:
            employee.save()
            
        return employee


class RoleForm(forms.ModelForm):
    """Form for creating and editing roles"""
    
    class Meta:
        model = Role
        fields = [
            'name', 'description', 'can_manage_properties', 'can_manage_landlords',
            'can_manage_residents', 'can_handle_payments', 'can_manage_employees',
            'can_view_reports', 'can_handle_maintenance', 'can_handle_support_tickets',
            'can_manage_leads', 'can_manage_housekeeping', 'can_access_crm'
        ]
        widgets = {
            'name': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            }),
            'description': forms.Textarea(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
                'rows': 3,
                'placeholder': 'Describe the role responsibilities and scope'
            }),
            'can_manage_properties': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_manage_landlords': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_manage_residents': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_handle_payments': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_manage_employees': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_view_reports': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_handle_maintenance': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_handle_support_tickets': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_manage_leads': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_manage_housekeeping': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
            'can_access_crm': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check if role name already exists (excluding current role if editing)
            existing_role = Role.objects.filter(name=name)
            if self.instance and self.instance.pk:
                existing_role = existing_role.exclude(pk=self.instance.pk)
            
            if existing_role.exists():
                raise ValidationError("A role with this name already exists.")
        return name


class EmployeeStatusForm(forms.Form):
    """Simple form for updating employee status"""
    STATUS_CHOICES = Employee.EMPLOYMENT_STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )


class EmployeeSearchForm(forms.Form):
    """Form for searching and filtering employees"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Search by name, ID, email...'
        })
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="All Roles",
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Employee.EMPLOYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    employment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Employee.EMPLOYMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )