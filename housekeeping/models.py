
# housekeeping/models.py
from django.db import models
from django.utils import timezone

class HousekeepingSchedule(models.Model):
    """Scheduled housekeeping for properties"""
    SCHEDULE_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('one_time', 'One-time'),
        ('move_out_cleaning', 'Move-out Cleaning'),
        ('deep_cleaning', 'Deep Cleaning'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    schedule_id = models.CharField(max_length=20, unique=True)
    
    # Property Information
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='housekeeping_schedules')
    room = models.ForeignKey('properties.Room', on_delete=models.CASCADE, null=True, blank=True)
    
    # Schedule Details
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    estimated_duration = models.DurationField(help_text="Estimated time to complete")
    
    # Assignment
    assigned_staff = models.ManyToManyField('employees.Employee', related_name='housekeeping_assignments')
    supervisor = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_housekeeping')
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    started_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    
    # Tasks and Quality Control
    checklist_completed = models.BooleanField(default=False)
    quality_check_passed = models.BooleanField(default=False)
    quality_checked_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='quality_checked_housekeeping')
    
    # Documentation
    before_photos = models.FileField(upload_to='housekeeping_photos/', null=True, blank=True)
    after_photos = models.FileField(upload_to='housekeeping_photos/', null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    issues_found = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"Housekeeping {self.schedule_id} - {self.property.name}"
