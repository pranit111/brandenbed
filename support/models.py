
# support/models.py
from django.db import models
from django.utils import timezone

class SupportCategory(models.Model):
    """Categories for support tickets based on BrandenBed operations"""
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance & Repairs'),
        ('housekeeping', 'Housekeeping'),
        ('amenities', 'Amenities (WiFi, Power, etc.)'),
        ('access_security', 'Access & Security'),
        ('billing', 'Billing & Payments'),
        ('room_issues', 'Room Issues'),
        ('neighbor_complaints', 'Neighbor Complaints'),
        ('contract', 'Contract & Legal'),
        ('move_in_out', 'Move In/Out'),
        ('general_inquiry', 'General Inquiry'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=25, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    priority_level = models.PositiveIntegerField(default=3, help_text="1=High, 2=Medium, 3=Low")
    sla_hours = models.PositiveIntegerField(default=24, help_text="Service Level Agreement in hours")
    
    class Meta:
        verbose_name_plural = "Support Categories"
    
    def __str__(self):
        return self.get_name_display()

class SupportTicket(models.Model):
    """Support tickets from residents"""
    PRIORITY_CHOICES = [
        (1, 'Emergency'),
        (2, 'High'),
        (3, 'Medium'),
        (4, 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_resident', 'Waiting for Resident'),
        ('escalated', 'Escalated'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    ticket_id = models.CharField(max_length=20, unique=True)
    
    # Ticket Information
    resident = models.ForeignKey('residents.Resident', on_delete=models.CASCADE, related_name='support_tickets')
    property_ref = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    room = models.ForeignKey('properties.Room', on_delete=models.CASCADE, null=True, blank=True)
    
    # Ticket Details
    category = models.ForeignKey(SupportCategory, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES, default=3)
    
    # Status and Assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    
    # SLA Tracking
    sla_due_date = models.DateTimeField(null=True, blank=True)
    first_response_time = models.DateTimeField(null=True, blank=True)
    resolution_time = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_tickets')
    
    # Cost Tracking (for maintenance/repairs)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Follow-up
    requires_followup = models.BooleanField(default=False)
    followup_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.subject}"
    
    @property
    def is_overdue(self):
        if self.sla_due_date and self.status not in ['resolved', 'closed']:
            return timezone.now() > self.sla_due_date
        return False
    
    def save(self, *args, **kwargs):
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()
        
        # Set SLA due date based on category
        if not self.sla_due_date and self.category:
            self.sla_due_date = self.created_at + timezone.timedelta(hours=self.category.sla_hours)
        
        super().save(*args, **kwargs)

class TicketComment(models.Model):
    """Comments and updates on support tickets"""
    COMMENT_TYPE_CHOICES = [
        ('internal', 'Internal Note'),
        ('resident_response', 'Response to Resident'),
        ('status_update', 'Status Update'),
        ('escalation', 'Escalation Note'),
    ]
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPE_CHOICES, default='internal')
    comment = models.TextField()
    
    # Visibility
    is_internal = models.BooleanField(default=True, help_text="Internal notes are not visible to residents")
    
    # Attachments
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_id} by {self.author.user.username}"
