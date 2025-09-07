# residents/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Resident(models.Model):
    """Students and professionals living in BrandenBed properties"""
    RESIDENT_TYPE_CHOICES = [
        ('student', 'International Student'),
        ('local_student', 'Local Student'),
        ('professional', 'Working Professional'),

    ]
    
    RESIDENT_STATUS_CHOICES = [
        ('lead', 'Lead'),
        ('applied', 'Application Submitted'),
        ('verified', 'Verification Complete'),
        ('active', 'Active Resident'),
        ('moved_out', 'Moved Out'),
        ('terminated', 'Terminated'),
    ]
    
    IDENTIFICATION_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID Card'),
        ('student_id', 'Student ID'),
        ('visa', 'Visa'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resident_id = models.CharField(max_length=20, unique=True)
    
    # Personal Information
    resident_type = models.CharField(max_length=20, choices=RESIDENT_TYPE_CHOICES)
    identification_type = models.CharField(max_length=15, choices=IDENTIFICATION_TYPE_CHOICES)
    identification_number = models.CharField(max_length=50)
    
    # Academic/Professional Information
    university = models.CharField(max_length=200, blank=True)
    course = models.CharField(max_length=200, blank=True)
    enrollment_proof = models.FileField(upload_to='resident_documents/', null=True, blank=True)
    
    employer = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    employment_proof = models.FileField(upload_to='resident_documents/', null=True, blank=True)
    
    # Financial Information
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    income_source = models.CharField(max_length=100, blank=True, help_text="e.g., Job, Scholarship, Family Support")
    
    # Visa and Legal Status (for international residents)
    visa_type = models.CharField(max_length=50, blank=True)
    visa_expiry = models.DateField(null=True, blank=True)
    
    # Preferences
    preferred_room_type = models.CharField(max_length=50, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)
    budget_range = models.CharField(max_length=50, blank=True, help_text="e.g., 400-600 EUR")
    
    # Residency Details
    current_property = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, null=True, blank=True)
    current_room = models.ForeignKey('properties.Room', on_delete=models.SET_NULL, null=True, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(null=True, blank=True)
    
    # Status and Management
    status = models.CharField(max_length=15, choices=RESIDENT_STATUS_CHOICES, default='lead')
    assigned_support_agent = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Emergency Contact (Additional to user model)
    parent_guardian_name = models.CharField(max_length=100, blank=True)
    parent_guardian_phone = models.CharField(max_length=17, blank=True)
    parent_guardian_email = models.EmailField(blank=True)
    
    # Special Requirements
    dietary_requirements = models.CharField(max_length=200, blank=True)
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions we should know about")
    special_needs = models.TextField(blank=True)
    
    # Onboarding Progress
    verification_completed = models.BooleanField(default=False)
    deposit_paid = models.BooleanField(default=False)
    agreement_signed = models.BooleanField(default=False)
    orientation_completed = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.resident_id} - {self.user.get_full_name()}"
    
    @property
    def is_international(self):
        return self.resident_type in ['student', 'intern'] and self.user.nationality != 'German'

class ResidencyContract(models.Model):
    """Rental agreements for residents"""
    CONTRACT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent_for_signing', 'Sent for Signing'),
        ('signed', 'Signed'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ]
    
    contract_id = models.CharField(max_length=20, unique=True)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='contracts')
    property_ref = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    room = models.ForeignKey('properties.Room', on_delete=models.CASCADE)
    
    # Contract Terms
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Fees
    admin_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    cleaning_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Contract Details
    notice_period_days = models.PositiveIntegerField(default=30)
    utilities_included = models.BooleanField(default=True)
    
    # Status and Signing
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES, default='draft')
    signed_date = models.DateTimeField(null=True, blank=True)
    contract_file = models.FileField(upload_to='contracts/', null=True, blank=True)
    
    # Management
    created_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)
    
    terms_and_conditions = models.TextField(blank=True)
    special_clauses = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Contract {self.contract_id} - {self.resident}"
    
    @property
    def is_active(self):
        try:
            # Check if dates are available
            if not all([self.start_date, self.end_date]):
                return False
            
            today = timezone.now().date()
            return self.start_date <= today <= self.end_date and self.status == 'active'
        except (TypeError, ValueError):
            # Handle any potential errors with date comparison
            return False
        
    @property
    def days_remaining(self):
        if self.status == 'active':
            return (self.end_date - timezone.now().date()).days
        return 0
