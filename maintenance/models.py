# maintenance/models.py
from django.db import models
from django.utils import timezone

from support.models import SupportTicket

class Vendor(models.Model):
    """External vendors for maintenance and services"""
    VENDOR_TYPE_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('hvac', 'HVAC'),
        ('cleaning', 'Cleaning Services'),
        ('security', 'Security Systems'),
        ('general_maintenance', 'General Maintenance'),
        ('appliance_repair', 'Appliance Repair'),
        ('pest_control', 'Pest Control'),
        ('landscaping', 'Landscaping'),
        ('other', 'Other'),
    ]
    
    VENDOR_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    vendor_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    vendor_type = models.CharField(max_length=25, choices=VENDOR_TYPE_CHOICES)
    
    # Contact Information
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=17)
    email = models.EmailField(blank=True)
    address = models.TextField()
    
    # Service Details
    services_offered = models.TextField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    emergency_available = models.BooleanField(default=False)
    
    # Contract Information
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    
    # Performance Tracking
    status = models.CharField(max_length=15, choices=VENDOR_STATUS_CHOICES, default='active')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, help_text="Rating out of 5.00")
    total_jobs_completed = models.PositiveIntegerField(default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vendor_id} - {self.name}"

class MaintenanceRequest(models.Model):
    """Maintenance and repair requests"""
    REQUEST_TYPE_CHOICES = [
        ('routine', 'Routine Maintenance'),
        ('repair', 'Repair'),
        ('emergency', 'Emergency'),
        ('inspection', 'Inspection'),
        ('upgrade', 'Upgrade'),
    ]
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('assigned', 'Assigned to Vendor'),
        ('in_progress', 'Work in Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    request_id = models.CharField(max_length=20, unique=True)
    
    # Request Information
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='maintenance_requests')
    room = models.ForeignKey('properties.Room', on_delete=models.CASCADE, null=True, blank=True)
    support_ticket = models.OneToOneField(SupportTicket, on_delete=models.CASCADE, null=True, blank=True)
    
    # Request Details
    request_type = models.CharField(max_length=15, choices=REQUEST_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.PositiveIntegerField(choices=[(1, 'Emergency'), (2, 'High'), (3, 'Medium'), (4, 'Low')], default=3)
    
    # Assignment
    assigned_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status and Timing
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    scheduled_date = models.DateTimeField(null=True, blank=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Cost Tracking
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Documentation
    before_photos = models.FileField(upload_to='maintenance_photos/', null=True, blank=True)
    after_photos = models.FileField(upload_to='maintenance_photos/', null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    
    # Management
    requested_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, related_name='requested_maintenance')
    approved_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_maintenance')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"Maintenance {self.request_id} - {self.title}"
