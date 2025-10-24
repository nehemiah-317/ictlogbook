from django.contrib import admin
from .models import AssetRecord


@admin.register(AssetRecord)
class AssetRecordAdmin(admin.ModelAdmin):
    list_display = ('staff_name', 'staff_id', 'asset_type', 'division', 'status', 'recorded_by', 'timestamp')
    list_filter = ('status', 'asset_type', 'division', 'timestamp', 'recorded_by')
    search_fields = ('staff_name', 'staff_id', 'asset_type', 'division', 'phone_number', 'problem_reported')
    readonly_fields = ('timestamp', 'returned_at')
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('staff_name', 'staff_id', 'phone_number', 'division')
        }),
        ('Asset Details', {
            'fields': ('asset_type', 'problem_reported', 'status', 'signature')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Tracking Information', {
            'fields': ('recorded_by', 'timestamp', 'returned_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set recorded_by to current user if not set"""
        if not obj.pk:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Filter queryset based on user group"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return qs
        return qs.filter(recorded_by=request.user)

