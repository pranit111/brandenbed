# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Extended user model for employees, landlords, and residents"""
    USER_TYPE_CHOICES = [
        ('employee', 'Employee'),
        ('landlord', 'Landlord/Property Owner'),
        ('resident', 'Student/Professional Resident'),
        ('lead', 'Potential Resident Lead'),
    ]
    
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    whatsapp_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=200, blank=True)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='Germany')
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Communication Preferences
    preferred_language = models.CharField(max_length=50, default='English')
    marketing_consent = models.BooleanField(default=False)
    whatsapp_consent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"
