
# employees/models.py
from django.db import models
from django.conf import settings

class Role(models.Model):
    """Employee roles with specific permissions for BrandenBed operations"""
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('manager', 'Operations Manager'),
        ('property_manager', 'Property Manager'),
        ('maintenance_supervisor', 'Maintenance Supervisor'),
        ('support_agent', 'Customer Support Agent'),
        ('sales_executive', 'Business Development Executive'),
        ('accountant', 'Accountant'),
        ('housekeeping_supervisor', 'Housekeeping Supervisor'),
        ('maintenance_technician', 'Maintenance Technician'),
        ('housekeeping_staff', 'Housekeeping Staff'),
    ]
    
    name = models.CharField(max_length=30, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    # Permissions for different modules
    can_manage_properties = models.BooleanField(default=False)
    can_manage_landlords = models.BooleanField(default=False)
    can_manage_residents = models.BooleanField(default=False)
    can_handle_payments = models.BooleanField(default=False)
    can_manage_employees = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_handle_maintenance = models.BooleanField(default=False)
    can_handle_support_tickets = models.BooleanField(default=False)
    can_manage_leads = models.BooleanField(default=False)
    can_manage_housekeeping = models.BooleanField(default=False)
    can_access_crm = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()

class Employee(models.Model):
    """Employee profiles for BrandenBed staff"""
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    employment_type = models.CharField(max_length=15, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    employment_status = models.CharField(max_length=15, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    
    # Hierarchy
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Employment Details
    hire_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    
    # Compensation
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Work Details
    work_location = models.CharField(max_length=100, blank=True, help_text="Primary work location/property")
    shift_timing = models.CharField(max_length=50, blank=True)
    
    # Skills and Certifications
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    certifications = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
    
    @property
    def is_manager(self):
        return Employee.objects.filter(manager=self).exists()
