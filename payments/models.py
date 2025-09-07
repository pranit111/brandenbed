# payments/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal

class PaymentType(models.Model):
    """Different types of payments in BrandenBed system"""
    TYPE_CHOICES = [
        ('rent', 'Monthly Rent'),
        ('security_deposit', 'Security Deposit'),
        ('admin_fee', 'Admin Fee'),
        ('cleaning_fee', 'Cleaning Fee'),
        ('maintenance_fee', 'Maintenance Fee'),
        ('late_fee', 'Late Payment Fee'),
        ('utility_bill', 'Utility Bill'),
        ('damage_charge', 'Damage Charge'),
        ('refund', 'Refund'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=30, choices=TYPE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    default_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.get_name_display()

class Payment(models.Model):
    """All payment transactions - manual entry system"""
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('online_payment', 'Online Payment'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Payment Received'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('disputed', 'Under Dispute'),
    ]
    
    PAYMENT_DIRECTION_CHOICES = [
        ('inbound', 'Payment Received'),
        ('outbound', 'Payment Made'),
    ]
    
    payment_id = models.CharField(max_length=20, unique=True)
    
    # Payment Parties
    resident = models.ForeignKey('residents.Resident', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    landlord = models.ForeignKey('landlords.Landlord', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Property Information
    property_ref = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    room = models.ForeignKey('properties.Room', on_delete=models.CASCADE, null=True, blank=True)
    
    # Payment Details
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    direction = models.CharField(max_length=10, choices=PAYMENT_DIRECTION_CHOICES, default='inbound')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Transaction Information
    transaction_id = models.CharField(max_length=100, blank=True, help_text="External transaction reference")
    transaction_date = models.DateTimeField(default=timezone.now)
    
    # Status Management
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment Period (for recurring payments)
    payment_period_start = models.DateField(null=True, blank=True)
    payment_period_end = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Staff Management
    recorded_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, related_name='recorded_payments')
    verified_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    
    # Documentation
    receipt_file = models.FileField(upload_to='payment_receipts/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        party = self.resident or self.landlord
        return f"{self.payment_id} - {party} - €{self.amount}"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status in ['pending']:
            return timezone.now().date() > self.due_date
        return False

class PaymentReminder(models.Model):
    """Automated and manual payment reminders"""
    REMINDER_TYPE_CHOICES = [
        ('upcoming', 'Payment Due Soon'),
        ('overdue', 'Payment Overdue'),
        ('final_notice', 'Final Notice'),
        ('custom', 'Custom Reminder'),
    ]
    
    REMINDER_METHOD_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Phone Call'),
        ('in_person', 'In-Person'),
    ]
    
    resident = models.ForeignKey('residents.Resident', on_delete=models.CASCADE, related_name='payment_reminders')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    
    # Reminder Details
    reminder_type = models.CharField(max_length=15, choices=REMINDER_TYPE_CHOICES)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    
    # Communication
    reminder_method = models.CharField(max_length=15, choices=REMINDER_METHOD_CHOICES, default='email')
    message_sent = models.TextField(blank=True)
    
    # Status
    sent_date = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Reminder - {self.resident} - €{self.amount_due} ({self.reminder_type})"
