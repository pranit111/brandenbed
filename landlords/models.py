
# landlords/models.py
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

class Landlord(models.Model):
    """Property owners who partner with BrandenBed"""
    PARTNERSHIP_STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('under_evaluation', 'Under Evaluation'),
        ('active', 'Active Partner'),
        ('inactive', 'Inactive'),
        ('terminated', 'Partnership Terminated'),
    ]
    
    LANDLORD_TYPE_CHOICES = [
        ('individual', 'Individual Owner'),
        ('company', 'Property Management Company'),
        ('investor', 'Real Estate Investor'),
        ('institutional', 'Institutional Owner'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    landlord_id = models.CharField(max_length=20, unique=True)
    
    # Business Information
    landlord_type = models.CharField(max_length=15, choices=LANDLORD_TYPE_CHOICES, default='individual')
    company_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=50, blank=True, help_text="German tax identification number")
    
    # Partnership Details
    partnership_status = models.CharField(max_length=20, choices=PARTNERSHIP_STATUS_CHOICES, default='prospect')
    partnership_start_date = models.DateField(null=True, blank=True)
    
    # Financial Information
    preferred_payout_schedule = models.CharField(max_length=50, default='Monthly', help_text="Preferred payout frequency")
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    
    # Relationship Management
    assigned_bd_executive = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, help_text="Business Development Executive")
    
    # Preferences
    guaranteed_rent_preference = models.BooleanField(default=False, help_text="Prefers guaranteed rent options")
    maintenance_handling = models.CharField(max_length=100, default='BrandenBed Managed', help_text="How maintenance should be handled")
    
    # Communication
    preferred_communication = models.CharField(max_length=50, default='Email')
    
    # Performance Metrics
    total_properties = models.PositiveIntegerField(default=0)
    total_earnings_to_date = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        name = self.company_name if self.company_name else self.user.get_full_name()
        return f"{self.landlord_id} - {name}"

class LandlordDocument(models.Model):
    """Documents related to landlords and partnerships"""
    DOCUMENT_TYPE_CHOICES = [
        ('property_deed', 'Property Deed'),
        ('tax_document', 'Tax Document'),
        ('bank_details', 'Bank Details'),
        ('partnership_agreement', 'Partnership Agreement'),
        ('identity_proof', 'Identity Proof'),
        ('other', 'Other'),
    ]
    
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=25, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='landlord_documents/')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.landlord} - {self.title}"
