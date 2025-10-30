from django.contrib import admin
from .models import SupportRecord


@admin.register(SupportRecord)
class SupportRecordAdmin(admin.ModelAdmin):
    list_display = ('staff_name', 'staff_id', 'issue_summary', 'status', 'recorded_by', 'timestamp', 'resolved_at')
    list_filter = ('status', 'timestamp', 'recorded_by')
    search_fields = ('staff_name', 'staff_id', 'issue_reported', 'phone_number')
    readonly_fields = ('timestamp', 'resolved_at')
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('staff_name', 'staff_id', 'phone_number')
        }),
        ('Issue Details', {
            'fields': ('issue_reported', 'status', 'notes')
        }),
        ('Tracking Information', {
            'fields': ('recorded_by', 'timestamp', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def issue_summary(self, obj):
        """Return truncated issue description"""
        return obj.issue_reported[:50] + '...' if len(obj.issue_reported) > 50 else obj.issue_reported
    issue_summary.short_description = 'Issue'
    
    def save_model(self, request, obj, form, change):
        """Auto-set recorded_by to current user if not set"""
        if not obj.pk:  # Only set on creation
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Filter queryset based on user group"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return qs
        # Non-admin users see only their records
        return qs.filter(recorded_by=request.user)

