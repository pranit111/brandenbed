# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from decimal import Decimal
from accounts.models import User

class CustomUserRegistrationForm(UserCreationForm):
    """Enhanced user registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
            'placeholder': _('Enter your email address')
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
            'placeholder': _('First Name')
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
            'placeholder': _('Last Name')
        })
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5'
        })
    )
    
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
            'placeholder': '+49 123 456 7890'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
                'placeholder': _('Choose a username')
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
                'placeholder': _('Create a password')
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
                'placeholder': _('Confirm your password')
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('A user with this email already exists.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user

# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    """Enhanced login form with remember me functionality"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
            'placeholder': _('Username or Email'),
            'id': 'id_username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-gold focus:border-brand-gold block w-full p-2.5 pl-10',
            'placeholder': _('Password'),
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-brand-gold bg-gray-100 border-gray-300 rounded focus:ring-brand-gold',
            'id': 'remember_me'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username


# profiles/forms.py
from django import forms
from django.contrib.auth import get_user_model
from accounts.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'whatsapp_number',
            'date_of_birth', 'nationality', 'profile_picture', 'address_line_1',
            'address_line_2', 'city', 'state', 'pincode', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'preferred_language', 'marketing_consent', 'whatsapp_consent'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }