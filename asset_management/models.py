from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AssetRecord(models.Model):
    """Model for tracking physical asset collection or handling"""
    
    # Status constants
    IN_USE = 'IN_USE'
    RETURNED = 'RETURNED'
    UNDER_REPAIR = 'UNDER_REPAIR'
    
    STATUS_CHOICES = [
        (IN_USE, 'In Use'),
        (RETURNED, 'Returned'),
        (UNDER_REPAIR, 'Under Repair'),
    ]
    
    staff_name = models.CharField(max_length=200, help_text="Person collecting/handling the asset")
    staff_id = models.CharField(max_length=50, help_text="Staff ID number")
    problem_reported = models.TextField(help_text="Reason for collection or issue with asset")
    asset_type = models.CharField(max_length=100, help_text="Type of asset/machine")
    division = models.CharField(max_length=100, help_text="Department or division")
    phone_number = models.CharField(max_length=20, help_text="Contact number")
    signature = models.CharField(
        max_length=200,
        blank=True,
        help_text="Digital signature or placeholder"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_USE,
        help_text="Current status of the asset"
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='asset_records',
        help_text="ICT staff who recorded this"
    )
    timestamp = models.DateTimeField(default=timezone.now, help_text="When this was recorded")
    returned_at = models.DateTimeField(null=True, blank=True, help_text="When the asset was returned")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Asset Record"
        verbose_name_plural = "Asset Records"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['staff_id']),
            models.Index(fields=['asset_type']),
        ]
    
    def __str__(self):
        return f"{self.staff_name} - {self.asset_type} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set returned_at when status changes to RETURNED
        if self.status == self.RETURNED and not self.returned_at:
            self.returned_at = timezone.now()
        super().save(*args, **kwargs)

