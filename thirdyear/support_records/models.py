from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SupportRecord(models.Model):
    """Model for ICT support records provided to staff"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('SOLVED', 'Solved'),
    ]
    
    staff_name = models.CharField(max_length=200, help_text="Name of the staff assisted")
    staff_id = models.CharField(max_length=50, help_text="Staff ID number")
    issue_reported = models.TextField(help_text="Description of the problem")
    phone_number = models.CharField(max_length=20, help_text="Staff contact number")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the issue"
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='support_records',
        help_text="ICT staff who recorded this"
    )
    timestamp = models.DateTimeField(default=timezone.now, help_text="When this was recorded")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the issue was resolved")
    notes = models.TextField(blank=True, help_text="Additional notes or resolution details")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Support Record"
        verbose_name_plural = "Support Records"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['staff_id']),
        ]
    
    def __str__(self):
        return f"{self.staff_name} - {self.issue_reported[:50]} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set resolved_at when status changes to SOLVED
        if self.status == 'SOLVED' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

