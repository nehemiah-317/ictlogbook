from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ThermalRollRecord(models.Model):
    """Model for managing thermal roll collection by vendors"""
    
    vendor_name = models.CharField(max_length=200, help_text="Vendor or station name")
    cashier_owner_name = models.CharField(max_length=200, help_text="Contact person (cashier/owner)")
    quantity = models.PositiveIntegerField(help_text="Number of thermal rolls collected")
    phone_number = models.CharField(max_length=20, help_text="Contact number")
    signature = models.CharField(
        max_length=200,
        blank=True,
        help_text="Digital signature placeholder"
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='thermal_roll_records',
        help_text="ICT staff who recorded this"
    )
    timestamp = models.DateTimeField(default=timezone.now, help_text="When this was recorded")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Thermal Roll Record"
        verbose_name_plural = "Thermal Roll Records"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['vendor_name']),
        ]
    
    def __str__(self):
        return f"{self.vendor_name} - {self.quantity} rolls on {self.timestamp.date()}"
    
    @property
    def collection_date(self):
        """Return just the date part of timestamp"""
        return self.timestamp.date()

