from django.contrib import admin
from .models import VendorAssistance


@admin.register(VendorAssistance)
class VendorAssistanceAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'cashier_owner_name', 'problem_summary', 'status', 'resolved_by', 'timestamp')
    list_filter = ('status', 'timestamp', 'resolved_by')
    search_fields = ('company_name', 'cashier_owner_name', 'phone_number', 'problem_reported')
    readonly_fields = ('timestamp', 'resolved_at')
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('Vendor Information', {
            'fields': ('company_name', 'cashier_owner_name', 'phone_number')
        }),
        ('Issue Details', {
            'fields': ('problem_reported', 'status', 'resolution_notes')
        }),
        ('Tracking Information', {
            'fields': ('resolved_by', 'timestamp', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def problem_summary(self, obj):
        """Return truncated problem description"""
        return obj.problem_reported[:50] + '...' if len(obj.problem_reported) > 50 else obj.problem_reported
    problem_summary.short_description = 'Problem'
    
    def save_model(self, request, obj, form, change):
        """Auto-set resolved_by to current user if not set"""
        if not obj.pk:
            obj.resolved_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Filter queryset based on user group"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return qs
        return qs.filter(resolved_by=request.user)

