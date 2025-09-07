# leads/models.py
from django.db import models
from django.utils import timezone
from django.urls import reverse

class Lead(models.Model):
    """Potential customers who have inquired about our services"""
    
    LEAD_TYPE_CHOICES = [
        ('tenant', 'Tenant Inquiry'),
        ('landlord', 'Landlord Partnership'),
        ('contact', 'General Contact'),
    ]
    
    LEAD_SOURCE_CHOICES = [
        ('website_contact', 'Website Contact Form'),
        ('website_landlord', 'Website Landlord Form'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('university_partnership', 'University Partnership'),
        ('agent', 'Education Agent'),
        ('walk_in', 'Walk-in'),
        ('phone_call', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('other', 'Other'),
    ]
    
    LEAD_STATUS_CHOICES = [
        ('new', 'New Lead'),
        ('contacted', 'Initial Contact Made'),
        ('interested', 'Showing Interest'),
        ('meeting_scheduled', 'Meeting/Call Scheduled'),
        ('proposal_sent', 'Proposal/Information Sent'),
        ('converted', 'Converted'),
        ('lost', 'Lost Lead'),
        ('not_interested', 'Not Interested'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('shared_apartment', 'Shared Apartment'),
        ('student_residence', 'Student Residence'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES, default='contact')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=17, blank=True)
    company_name = models.CharField(max_length=200, blank=True, help_text="For landlord inquiries")
    
    # Lead Source and Attribution
    source = models.CharField(max_length=25, choices=LEAD_SOURCE_CHOICES, default='website_contact')
    source_details = models.CharField(max_length=200, blank=True, help_text="Specific source details")
    referrer_name = models.CharField(max_length=100, blank=True)
    
    # Inquiry Details
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(help_text="Main inquiry message")
    
    # For Landlord Leads
    property_address = models.TextField(blank=True, help_text="Full property address")
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPE_CHOICES, blank=True)
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True)
    monthly_rent_expectation = models.CharField(max_length=50, blank=True, help_text="Expected monthly rent")
    property_description = models.TextField(blank=True)
    
    # For Tenant Leads (minimal info)
    preferred_location = models.CharField(max_length=100, blank=True)
    budget_range = models.CharField(max_length=50, blank=True, help_text="e.g., 400-600 EUR")
    move_in_date = models.DateField(null=True, blank=True)
    
    # Lead Management
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Follow-up Information
    last_contact_date = models.DateTimeField(null=True, blank=True)
    next_followup_date = models.DateTimeField(null=True, blank=True)
    contact_attempts = models.PositiveIntegerField(default=0)
    
    # Conversion Tracking
    is_converted = models.BooleanField(default=False)
    conversion_date = models.DateTimeField(null=True, blank=True)
    lost_reason = models.CharField(max_length=200, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['assigned_to', '-created_at']),
            models.Index(fields=['lead_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.get_lead_type_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def days_since_last_contact(self):
        if self.last_contact_date:
            return (timezone.now() - self.last_contact_date).days
        return (timezone.now() - self.created_at).days
    
    @property
    def days_since_created(self):
        return (timezone.now() - self.created_at).days
    
    def get_absolute_url(self):
        return reverse('leads:lead_detail', kwargs={'pk': self.pk})


class LeadActivity(models.Model):
    """Track all activities and interactions with leads"""
    ACTIVITY_TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp Message'),
        ('meeting', 'In-Person Meeting'),
        ('video_call', 'Video Call'),
        ('property_visit', 'Property Visit'),
        ('proposal_sent', 'Proposal Sent'),
        ('follow_up', 'Follow-up'),
        ('note', 'Internal Note'),
        ('status_change', 'Status Change'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Activity Details
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    # Staff Member
    handled_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Lead Activities"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.lead.full_name} - {self.get_activity_type_display()} - {self.subject}"


class LeadSource(models.Model):
    """Track performance of different lead sources"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Tracking fields
    total_leads = models.PositiveIntegerField(default=0)
    converted_leads = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def conversion_rate(self):
        if self.total_leads > 0:
            return round((self.converted_leads / self.total_leads) * 100, 2)
        return 0