from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VendorAssistance(models.Model):
    """Model for recording technical support provided to external vendors"""
    
    # Status constants
    PENDING = 'PENDING'
    ONGOING = 'ONGOING'
    RESOLVED = 'RESOLVED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ONGOING, 'Ongoing'),
        (RESOLVED, 'Resolved'),
    ]
    
    company_name = models.CharField(max_length=200, help_text="Company or vendor name")
    cashier_owner_name = models.CharField(max_length=200, help_text="Contact person (cashier/owner)")
    problem_reported = models.TextField(help_text="Issue description")
    phone_number = models.CharField(max_length=20, help_text="Contact number")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Current status"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='vendor_assistance_records',
        help_text="ICT officer who handled this"
    )
    timestamp = models.DateTimeField(default=timezone.now, help_text="When this was recorded")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the issue was resolved")
    resolution_notes = models.TextField(blank=True, help_text="Resolution details")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Vendor Assistance Record"
        verbose_name_plural = "Vendor Assistance Records"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['company_name']),
        ]
    
    def __str__(self):
        return f"{self.company_name} - {self.problem_reported[:50]} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set resolved_at when status changes to RESOLVED
        if self.status == self.RESOLVED and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

