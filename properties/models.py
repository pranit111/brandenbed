# properties/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

class Property(models.Model):
    """Properties managed by BrandenBed"""
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('family_house', 'Family House'),
        ('residential_building', 'Residential Building'),
        ('student_residence', 'Student Residence'),
        ('co_living_space', 'Co-living Space'),
    ]
    
    FURNISHING_CHOICES = [
        ('furnished', 'Furnished'),
        ('semi_furnished', 'Semi-furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    
    PROPERTY_STATUS_CHOICES = [
        ('active', 'Active'),
        ('under_evaluation', 'Under Evaluation'),
        ('under_renovation', 'Under Renovation'),
        ('inactive', 'Inactive'),
        ('terminated', 'Partnership Terminated'),
    ]
    
    # Basic Information
    property_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    property_type = models.CharField(max_length=25, choices=PROPERTY_TYPE_CHOICES)
    furnishing = models.CharField(max_length=15, choices=FURNISHING_CHOICES, default='furnished')
    
    # Address
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, default='Berlin')
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10)
    
    # Berlin-specific location details
    district = models.CharField(max_length=100, blank=True, help_text="Berlin district (e.g., Mitte, Kreuzberg)")
    nearest_university = models.CharField(max_length=200, blank=True)
    distance_to_university = models.CharField(max_length=50, blank=True, help_text="e.g., 10 mins walk, 15 mins by U-Bahn")
    
    # Property Details
    total_rooms = models.PositiveIntegerField()
    total_beds = models.PositiveIntegerField()
    total_washrooms = models.PositiveIntegerField()
    total_area = models.DecimalField(max_digits=8, decimal_places=2, help_text="Area in square meters")
    year_built = models.PositiveIntegerField(null=True, blank=True)
    
    # Availability
    available_from = models.DateField()
    
    # Amenities - Core BrandenBed Features
    has_wifi = models.BooleanField(default=True, help_text="High-speed WiFi")
    has_security = models.BooleanField(default=True, help_text="24/7 security & support")
    has_power_backup = models.BooleanField(default=True, help_text="24/7 Power Backup")
    has_work_desk = models.BooleanField(default=True, help_text="Dedicated Work Desk")
    has_shared_kitchen = models.BooleanField(default=True)
    has_shared_lounge = models.BooleanField(default=True)
    has_laundry = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_elevator = models.BooleanField(default=False)
    
    # Transport Connectivity
    near_public_transport = models.BooleanField(default=True)
    nearest_metro_station = models.CharField(max_length=100, blank=True)
    distance_to_metro = models.CharField(max_length=50, blank=True, help_text="Walking distance to nearest station")
    
    # Management
    property_manager = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    housekeeping_supervisor = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_properties')
    maintenance_supervisor = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintained_properties')
    
    # Partnership Details
    landlord = models.ForeignKey('landlords.Landlord', on_delete=models.CASCADE, related_name='properties')
    partnership_start_date = models.DateField()
    partnership_end_date = models.DateField(null=True, blank=True)
    
    # Financial
    expected_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, help_text="Expected monthly rent in EUR")
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Property Status
    status = models.CharField(max_length=20, choices=PROPERTY_STATUS_CHOICES, default='under_evaluation')
    
    # Additional Information
    additional_notes = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True, help_text="Any special requirements for residents")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Properties"
    
    def __str__(self):
        return f"{self.property_id} - {self.name}"
    
    @property
    def total_capacity(self):
        return self.rooms.aggregate(total=models.Sum('max_occupants'))['total'] or 0
    
    @property
    def occupied_beds(self):
        return self.rooms.filter(status='occupied').aggregate(total=models.Sum('current_occupants'))['total'] or 0





class Room(models.Model):
    """Individual rooms within properties"""
    ROOM_TYPE_CHOICES = [
        ('private', 'Private Room'),
        ('shared', 'Shared Room'),
        ('studio', 'Studio Apartment'),
        ('single', 'Single Occupancy'),
        ('double', 'Double Occupancy'),
    ]
    
    ROOM_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('blocked', 'Blocked'),
    ]
    
    # Core fields
    property_ref = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=15, choices=ROOM_TYPE_CHOICES)
    
    # Room Specifications
    area = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Room area in square meters"
    )
    max_occupants = models.PositiveIntegerField(default=1)
    current_occupants = models.PositiveIntegerField(default=0)
    
    # Room Features - BrandenBed Standard
    has_private_bathroom = models.BooleanField(default=False)
    has_work_desk = models.BooleanField(default=True, help_text="Dedicated work desk")
    has_storage = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=False)
    has_window = models.BooleanField(default=True)
    
    # Pricing
    monthly_rent = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        help_text="Monthly rent in EUR"
    )
    utilities_included = models.BooleanField(default=True, help_text="All utilities included in rent")
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Availability
    status = models.CharField(max_length=15, choices=ROOM_STATUS_CHOICES, default='available')
    available_from = models.DateField()
    
    # Contract Details
    min_contract_duration = models.PositiveIntegerField(
        default=6, 
        help_text="Minimum contract duration in months"
    )
    max_contract_duration = models.PositiveIntegerField(
        default=12, 
        help_text="Maximum contract duration in months"
    )
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property_ref', 'room_number']
        ordering = ['room_number']
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
    
    def __str__(self):
        return f"{self.property_ref.name} - Room {self.room_number}"
    
    def clean(self):
        """Custom validation logic"""
        from django.core.exceptions import ValidationError
        from datetime import date
        
        errors = {}
        
        # Validate current occupants doesn't exceed max occupants
        if self.current_occupants > self.max_occupants:
            errors['current_occupants'] = 'Current occupants cannot exceed maximum occupants.'
        
        # Validate contract durations
        if self.min_contract_duration > self.max_contract_duration:
            errors['max_contract_duration'] = 'Maximum contract duration must be greater than or equal to minimum duration.'
        
        # Validate available_from date is not in the past for new rooms
        if not self.pk and self.available_from and self.available_from < date.today():
            errors['available_from'] = 'Available from date cannot be in the past.'
        
        # Validate room number uniqueness within property
        if self.property_ref_id and self.room_number:
            existing_rooms = Room.objects.filter(
                property_ref=self.property_ref, 
                room_number=self.room_number
            )
            if self.pk:
                existing_rooms = existing_rooms.exclude(pk=self.pk)
                
            if existing_rooms.exists():
                errors['room_number'] = f'Room number {self.room_number} already exists in this property.'
        
        # Validate area
        if self.area and self.area < 5:
            errors['area'] = 'Room area must be at least 5 square meters.'
        
        # Validate rent
        if self.monthly_rent and self.monthly_rent < 50:
            errors['monthly_rent'] = 'Monthly rent must be at least €50.'
        
        # Validate deposit
        if self.security_deposit and self.security_deposit < 0:
            errors['security_deposit'] = 'Security deposit cannot be negative.'
        
        # Validate occupants based on room type
        if self.room_type == 'single' and self.max_occupants > 1:
            errors['max_occupants'] = 'Single occupancy rooms can only have 1 occupant.'
        elif self.room_type == 'double' and self.max_occupants > 2:
            errors['max_occupants'] = 'Double occupancy rooms can have at most 2 occupants.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and formatting"""
        # Format room number
        if self.room_number:
            self.room_number = self.room_number.strip().upper()
        
        # Validate before saving
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        """Check if room is available for booking"""
        from datetime import date
        return (
            self.status == 'available' and 
            self.current_occupants < self.max_occupants and
            self.available_from <= date.today()
        )
    
    @property
    def occupancy_rate(self):
        """Calculate occupancy rate as percentage"""
        if self.max_occupants == 0:
            return 0
        return (self.current_occupants / self.max_occupants) * 100
    
    @property
    def is_fully_occupied(self):
        """Check if room is at maximum capacity"""
        return self.current_occupants >= self.max_occupants
    
    def get_absolute_url(self):
        """Return the URL for this room"""
        from django.urls import reverse
        return reverse('properties:room_detail', args=[self.property_ref.id, self.id])




















