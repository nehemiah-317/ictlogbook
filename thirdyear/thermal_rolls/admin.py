from django.contrib import admin
from .models import ThermalRollRecord


@admin.register(ThermalRollRecord)
class ThermalRollRecordAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'cashier_owner_name', 'quantity', 'phone_number', 'recorded_by', 'timestamp')
    list_filter = ('timestamp', 'recorded_by', 'vendor_name')
    search_fields = ('vendor_name', 'cashier_owner_name', 'phone_number')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('Vendor Information', {
            'fields': ('vendor_name', 'cashier_owner_name', 'phone_number')
        }),
        ('Collection Details', {
            'fields': ('quantity', 'signature', 'notes')
        }),
        ('Tracking Information', {
            'fields': ('recorded_by', 'timestamp'),
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

