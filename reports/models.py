
# reports/models.py (For tracking business metrics)
from django.db import models

class PropertyPerformance(models.Model):
    """Monthly performance metrics for properties"""
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='performance_reports')
    
    # Time Period
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)])
    
    # Occupancy Metrics
    total_rooms = models.PositiveIntegerField()
    occupied_rooms = models.PositiveIntegerField()
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage")
    
    # Financial Metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Operational Metrics
    total_support_tickets = models.PositiveIntegerField(default=0)
    resolved_support_tickets = models.PositiveIntegerField(default=0)
    average_resolution_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Hours")
    
    # Maintenance Metrics
    maintenance_requests = models.PositiveIntegerField(default=0)
    maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['property', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.property.name} - {self.month}/{self.year}"
    
    # forms.py - Complete form system for BrandenBed
