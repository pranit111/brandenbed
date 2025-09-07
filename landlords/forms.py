# landlords/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
import re

from .models import Landlord, LandlordDocument
from employees.models import Employee


from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from employees.models import Employee
import re
from datetime import date
from .models import Landlord

User = get_user_model()

class LandlordForm(forms.ModelForm):
    """Form for creating and updating landlords"""

    # User fields
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter email address'
        })
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '+49 XXX XXXXXXX'
        })
    )

    # Address fields
    address_line_1 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Street address'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'City'
        })
    )
    pincode = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Postal code'
        })
    )

    class Meta:
        model = Landlord
        fields = [
            'landlord_type', 'company_name', 'tax_id', 'partnership_status',
            'partnership_start_date', 'preferred_payout_schedule',
            'bank_account_number', 'bank_name', 'iban', 'assigned_bd_executive',
            'guaranteed_rent_preference', 'maintenance_handling',
            'preferred_communication', 'notes'
        ]
        widgets = {
            'landlord_type': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter company name (if applicable)'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter German tax identification number'
            }),
            'partnership_status': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'partnership_start_date': forms.DateInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'preferred_payout_schedule': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'bank_account_number': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter account number'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter bank name'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'DE89 3704 0044 0532 0130 00'
            }),
            'assigned_bd_executive': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'maintenance_handling': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'preferred_communication': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Add any additional notes about this landlord...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate user fields if updating existing landlord
        if self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone_number'].initial = self.instance.user.phone_number
            self.fields['address_line_1'].initial = self.instance.user.address_line_1
            self.fields['city'].initial = self.instance.user.city
            self.fields['pincode'].initial = self.instance.user.pincode

        # Set up BD executive choices
        self.fields['assigned_bd_executive'].queryset = Employee.objects.filter(
            user__is_active=True,
            role__name__in=['admin', 'manager', 'property_manager', 'sales_executive']
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        self.fields['assigned_bd_executive'].required = False

        # Add choices for select fields
        self.fields['preferred_payout_schedule'].widget.choices = [
            ('Monthly', 'Monthly'),
            ('Quarterly', 'Quarterly'),
            ('Semi-Annually', 'Semi-Annually'),
            ('Annually', 'Annually'),
        ]

        self.fields['maintenance_handling'].widget.choices = [
            ('BrandenBed Managed', 'BrandenBed Managed'),
            ('Landlord Managed', 'Landlord Managed'),
            ('Shared Responsibility', 'Shared Responsibility'),
        ]

        self.fields['preferred_communication'].widget.choices = [
            ('Email', 'Email'),
            ('Phone', 'Phone'),
            ('WhatsApp', 'WhatsApp'),
            ('SMS', 'SMS'),
        ]

        # Make partnership start date required if status is active
        if self.instance.pk and self.instance.partnership_status == 'active':
            self.fields['partnership_start_date'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
            
        user_query = User.objects.filter(email=email)
        if self.instance.pk and self.instance.user:
            user_query = user_query.exclude(id=self.instance.user.id)

        if user_query.exists():
            raise ValidationError("A user with this email already exists.")

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic phone number validation
            phone_clean = re.sub(r'\s+', '', phone)
            if not re.match(r'^\+?[\d\-\(\)\s]{9,17}$', phone_clean):
                raise ValidationError("Please enter a valid phone number.")
        return phone

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        landlord_type = self.cleaned_data.get('landlord_type')

        if landlord_type == 'company' and not company_name:
            raise ValidationError("Company name is required for company type landlords.")

        return company_name

    def clean_tax_id(self):
        tax_id = self.cleaned_data.get('tax_id')
        if tax_id:
            tax_id_clean = tax_id.replace(' ', '').replace('-', '')
            if not re.match(r'^\d{11}$', tax_id_clean):
                raise ValidationError("Please enter a valid German tax identification number (11 digits).")
        return tax_id

    def clean_iban(self):
        iban = self.cleaned_data.get('iban')
        if iban:
            iban_clean = iban.replace(' ', '').replace('-', '').upper()
            if not re.match(r'^DE\d{20}$', iban_clean):
                raise ValidationError("Please enter a valid German IBAN (starts with DE followed by 20 digits).")
            return iban_clean
        return iban

    def clean_partnership_start_date(self):
        partnership_start_date = self.cleaned_data.get('partnership_start_date')
        partnership_status = self.cleaned_data.get('partnership_status')

        if partnership_status == 'active' and not partnership_start_date:
            raise ValidationError("Partnership start date is required for active partners.")

        if partnership_start_date and partnership_start_date > date.today():
            raise ValidationError("Partnership start date cannot be in the future.")

        return partnership_start_date

    from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from employees.models import Employee
import re
from datetime import date
from .models import Landlord

User = get_user_model()

class LandlordForm(forms.ModelForm):
    """Form for creating and updating landlords"""

    # User fields
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter email address'
        })
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '+49 XXX XXXXXXX'
        })
    )

    # Address fields
    address_line_1 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Street address'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'City'
        })
    )
    pincode = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Postal code'
        })
    )

    class Meta:
        model = Landlord
        fields = [
            'landlord_type', 'company_name', 'tax_id', 'partnership_status',
            'partnership_start_date', 'preferred_payout_schedule',
            'bank_account_number', 'bank_name', 'iban', 'assigned_bd_executive',
            'guaranteed_rent_preference', 'maintenance_handling',
            'preferred_communication', 'notes'
        ]
        widgets = {
            'landlord_type': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter company name (if applicable)'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter German tax identification number'
            }),
            'partnership_status': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'partnership_start_date': forms.DateInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'preferred_payout_schedule': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'bank_account_number': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter account number'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter bank name'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'DE89 3704 0044 0532 0130 00'
            }),
            'assigned_bd_executive': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'maintenance_handling': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'preferred_communication': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Add any additional notes about this landlord...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate user fields if updating existing landlord
        if self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone_number'].initial = self.instance.user.phone_number
            self.fields['address_line_1'].initial = self.instance.user.address_line_1
            self.fields['city'].initial = self.instance.user.city
            self.fields['pincode'].initial = self.instance.user.pincode

        # Set up BD executive choices
        self.fields['assigned_bd_executive'].queryset = Employee.objects.filter(
            user__is_active=True,
            role__name__in=['admin', 'manager', 'property_manager', 'sales_executive']
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        self.fields['assigned_bd_executive'].required = False

        # Add choices for select fields
        self.fields['preferred_payout_schedule'].widget.choices = [
            ('Monthly', 'Monthly'),
            ('Quarterly', 'Quarterly'),
            ('Semi-Annually', 'Semi-Annually'),
            ('Annually', 'Annually'),
        ]

        self.fields['maintenance_handling'].widget.choices = [
            ('BrandenBed Managed', 'BrandenBed Managed'),
            ('Landlord Managed', 'Landlord Managed'),
            ('Shared Responsibility', 'Shared Responsibility'),
        ]

        self.fields['preferred_communication'].widget.choices = [
            ('Email', 'Email'),
            ('Phone', 'Phone'),
            ('WhatsApp', 'WhatsApp'),
            ('SMS', 'SMS'),
        ]

        # Make partnership start date required if status is active
        if self.instance.pk and self.instance.partnership_status == 'active':
            self.fields['partnership_start_date'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
            
        user_query = User.objects.filter(email=email)
        if self.instance.pk and self.instance.user:
            user_query = user_query.exclude(id=self.instance.user.id)

        if user_query.exists():
            raise ValidationError("A user with this email already exists.")

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic phone number validation
            phone_clean = re.sub(r'\s+', '', phone)
            if not re.match(r'^\+?[\d\-\(\)\s]{9,17}$', phone_clean):
                raise ValidationError("Please enter a valid phone number.")
        return phone

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        landlord_type = self.cleaned_data.get('landlord_type')

        if landlord_type == 'company' and not company_name:
            raise ValidationError("Company name is required for company type landlords.")

        return company_name

    def clean_tax_id(self):
        tax_id = self.cleaned_data.get('tax_id')
        if tax_id:
            tax_id_clean = tax_id.replace(' ', '').replace('-', '')
            if not re.match(r'^\d{11}$', tax_id_clean):
                raise ValidationError("Please enter a valid German tax identification number (11 digits).")
        return tax_id

    def clean_iban(self):
        iban = self.cleaned_data.get('iban')
        if iban:
            iban_clean = iban.replace(' ', '').replace('-', '').upper()
            if not re.match(r'^DE\d{20}$', iban_clean):
                raise ValidationError("Please enter a valid German IBAN (starts with DE followed by 20 digits).")
            return iban_clean
        return iban

    def clean_partnership_start_date(self):
        partnership_start_date = self.cleaned_data.get('partnership_start_date')
        partnership_status = self.cleaned_data.get('partnership_status')

        if partnership_status == 'active' and not partnership_start_date:
            raise ValidationError("Partnership start date is required for active partners.")

        if partnership_start_date and partnership_start_date > date.today():
            raise ValidationError("Partnership start date cannot be in the future.")

        return partnership_start_date

    def save(self, commit=True):
        # Handle user creation/update
        user_data = {
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'email': self.cleaned_data['email'],
            'phone_number': self.cleaned_data.get('phone_number', ''),
            'address_line_1': self.cleaned_data.get('address_line_1', ''),
            'city': self.cleaned_data.get('city', ''),
            'pincode': self.cleaned_data.get('pincode', ''),
            'user_type': 'landlord'
        }
        
        # Check if this is a new landlord (no pk) or existing landlord without user
        try:
            existing_user = self.instance.user if self.instance.pk else None
        except User.DoesNotExist:
            existing_user = None
        
        if not existing_user:
            # Create new user
            username = self.cleaned_data['email']  # Use email as username
            user = User.objects.create_user(
                username=username,
                **user_data
            )
            self.instance.user = user
        else:
            # Update existing user
            user = existing_user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            if commit:
                user.save()

        return super().save(commit)





class LandlordDocumentForm(forms.ModelForm):
    """Form for uploading landlord documents"""
    
    class Meta:
        model = LandlordDocument
        fields = ['document_type', 'title', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document title or description'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.xls', '.xlsx']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError("File type not supported. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT, XLS, XLSX")
        
        return file
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters long.")
        return title.strip()

class LandlordFilterForm(forms.Form):
    """Form for filtering landlords in list view"""
    
    PARTNERSHIP_CHOICES = [('', 'All Statuses')] + Landlord.PARTNERSHIP_STATUS_CHOICES
    TYPE_CHOICES = [('', 'All Types')] + Landlord.LANDLORD_TYPE_CHOICES
    HAS_PROPERTIES_CHOICES = [
        ('', 'All'),
        ('yes', 'Has Properties'),
        ('no', 'No Properties')
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'Search by name, email, company, or landlord ID...'
        })
    )
    
    partnership_status = forms.ChoiceField(
        choices=PARTNERSHIP_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    landlord_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    assigned_bd_executive = forms.ModelChoiceField(
        queryset=Employee.objects.filter(
            user__is_active=True,
            role__name__in=['admin', 'manager', 'property_manager', 'sales_executive']
        ).select_related('user'),
        required=False,
        empty_label="All BD Executives",
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    has_properties = forms.ChoiceField(
        choices=HAS_PROPERTIES_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })
    )
    
    partnership_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'type': 'date'
        })
    )
    
    partnership_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('partnership_date_from')
        date_to = cleaned_data.get('partnership_date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("Start date cannot be after end date.")
        
        return cleaned_data

class PartnershipUpdateForm(forms.ModelForm):
    """Form for updating partnership status and related fields"""
    
    class Meta:
        model = Landlord
        fields = [
            'partnership_status', 'partnership_start_date', 
            'assigned_bd_executive', 'notes'
        ]
        widgets = {
            'partnership_status': forms.Select(attrs={'class': 'form-control'}),
            'partnership_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'assigned_bd_executive': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Update notes...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['assigned_bd_executive'].queryset = Employee.objects.filter(
            user__is_active=True,
            role__name__in=['admin', 'manager', 'property_manager', 'sales_executive'] 
        ).select_related('user').order_by('user__first_name', 'user__last_name')
        
        # Make fields optional
        self.fields['partnership_start_date'].required = False
        self.fields['assigned_bd_executive'].required = False
    
    def clean_partnership_start_date(self):
        partnership_start_date = self.cleaned_data.get('partnership_start_date')
        partnership_status = self.cleaned_data.get('partnership_status')
        
        if partnership_status == 'active' and not partnership_start_date:
            # Auto-set to today if not provided
            partnership_start_date = timezone.now().date()
        
        if partnership_start_date and partnership_start_date > date.today():
            raise ValidationError("Partnership start date cannot be in the future.")
        
        return partnership_start_date

class BulkLandlordActionForm(forms.Form):
    """Form for bulk actions on landlords"""
    
    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('assign_bd', 'Assign BD Executive'),
        ('update_status', 'Update Partnership Status'),
        ('export_selected', 'Export Selected')
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    bd_executive = forms.ModelChoiceField(
        queryset=Employee.objects.filter(
            user__is_active=True,
            role__name__in=['admin', 'manager', 'property_manager', 'sales_executive']
        ).select_related('user'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    partnership_status = forms.ChoiceField(
        choices=[('', 'Select Status')] + Landlord.PARTNERSHIP_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        
        if action == 'assign_bd' and not cleaned_data.get('bd_executive'):
            raise ValidationError("Please select a BD Executive to assign.")
        elif action == 'update_status' and not cleaned_data.get('partnership_status'):
            raise ValidationError("Please select a partnership status.")
        
        return cleaned_data

class LandlordPerformanceFilterForm(forms.Form):
    """Form for filtering landlord performance reports"""
    
    period = forms.ChoiceField(
        choices=[
            ('30', 'Last 30 Days'),
            ('90', 'Last 3 Months'),
            ('180', 'Last 6 Months'),
            ('365', 'Last Year'),
            ('custom', 'Custom Period')
        ],
        initial='90',
        widget=forms.Select(attrs={'class': 'form-control'})
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
    
    min_properties = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum properties'
        })
    )
    
    partnership_status = forms.MultipleChoiceField(
        choices=Landlord.PARTNERSHIP_STATUS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if period == 'custom':
            if not date_from or not date_to:
                raise ValidationError("Start and end dates are required for custom period.")
            if date_from > date_to:
                raise ValidationError("Start date cannot be after end date.")
        
        return cleaned_data

class LandlordContactForm(forms.Form):
    """Form for contacting landlords (bulk email/communication)"""
    
    COMMUNICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp')
    ]
    
    communication_type = forms.ChoiceField(
        choices=COMMUNICATION_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject line...'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Your message...'
        })
    )
    
    send_immediately = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    schedule_datetime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        send_immediately = cleaned_data.get('send_immediately')
        schedule_datetime = cleaned_data.get('schedule_datetime')
        
        if not send_immediately and not schedule_datetime:
            raise ValidationError("Please either send immediately or schedule a time.")
        
        if schedule_datetime and schedule_datetime <= timezone.now():
            raise ValidationError("Scheduled time must be in the future.")
        
        return cleaned_data
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        return message.strip()