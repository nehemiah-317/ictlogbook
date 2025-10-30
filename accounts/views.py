from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, f'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


@require_POST
def logout_view(request):
    """Simple logout view that only accepts POST from the navbar form."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """View and edit user profile"""
    user = request.user
    user_groups = user.groups.all()
    is_admin = user.groups.filter(name='Admin').exists()
    
    context = {
        'user': user,
        'user_groups': user_groups,
        'is_admin': is_admin,
    }
    return render(request, 'accounts/profile.html', context)


def dashboard_view(request):
    """Enhanced dashboard view with detailed statistics and charts"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    from django.utils import timezone
    from django.db.models import Count, Q
    from datetime import timedelta
    from itertools import chain
    from operator import attrgetter
    from support_records.models import SupportRecord
    from asset_management.models import AssetRecord
    from vendor_assistance.models import VendorAssistance
    from thermal_rolls.models import ThermalRollRecord
    
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    # Base querysets based on user role
    if is_admin:
        support_records = SupportRecord.objects.all()
        asset_records = AssetRecord.objects.all()
        vendor_records = VendorAssistance.objects.all()
        thermal_records = ThermalRollRecord.objects.all()
    else:
        support_records = SupportRecord.objects.filter(recorded_by=request.user)
        asset_records = AssetRecord.objects.filter(recorded_by=request.user)
        vendor_records = VendorAssistance.objects.filter(resolved_by=request.user)
        thermal_records = ThermalRollRecord.objects.filter(recorded_by=request.user)
    
    # Total counts
    support_count = support_records.count()
    asset_count = asset_records.count()
    vendor_count = vendor_records.count()
    thermal_count = thermal_records.count()
    total_count = support_count + asset_count + vendor_count + thermal_count
    
    # Status breakdowns for Support Records
    support_pending = support_records.filter(status='PENDING').count()
    support_in_progress = support_records.filter(status='IN_PROGRESS').count()
    support_solved = support_records.filter(status='SOLVED').count()
    
    # Status breakdowns for Asset Management
    asset_in_use = asset_records.filter(status='IN_USE').count()
    asset_returned = asset_records.filter(status='RETURNED').count()
    asset_under_repair = asset_records.filter(status='UNDER_REPAIR').count()
    
    # Status breakdowns for Vendor Assistance
    vendor_pending = vendor_records.filter(status='PENDING').count()
    vendor_ongoing = vendor_records.filter(status='ONGOING').count()
    vendor_resolved = vendor_records.filter(status='RESOLVED').count()
    
    # Recent activity (last 10 records across all modules)
    support_recent = support_records.order_by('-timestamp')[:10]
    asset_recent = asset_records.order_by('-timestamp')[:10]
    vendor_recent = vendor_records.order_by('-timestamp')[:10]
    thermal_recent = thermal_records.order_by('-timestamp')[:10]
    
    # Combine and sort all recent records
    all_recent = sorted(
        chain(support_recent, asset_recent, vendor_recent, thermal_recent),
        key=attrgetter('timestamp'),
        reverse=True
    )[:10]
    
    # Format recent activity for template
    recent_activity = []
    for record in all_recent:
        if isinstance(record, SupportRecord):
            recent_activity.append({
                'type': 'support',
                'icon': 'support',
                'title': f'Support: {record.staff_name} - {record.issue_reported[:50]}...',
                'url': f'/support/{record.pk}/',
                'timestamp': record.timestamp,
                'status': record.status
            })
        elif isinstance(record, AssetRecord):
            recent_activity.append({
                'type': 'asset',
                'icon': 'asset',
                'title': f'Asset: {record.staff_name} - {record.asset_type}',
                'url': f'/assets/{record.pk}/',
                'timestamp': record.timestamp,
                'status': record.status
            })
        elif isinstance(record, VendorAssistance):
            recent_activity.append({
                'type': 'vendor',
                'icon': 'vendor',
                'title': f'Vendor: {record.company_name}',
                'url': f'/vendors/{record.pk}/',
                'timestamp': record.timestamp,
                'status': record.status
            })
        elif isinstance(record, ThermalRollRecord):
            recent_activity.append({
                'type': 'thermal',
                'icon': 'thermal',
                'title': f'Thermal Rolls: {record.vendor_name} - {record.quantity} rolls',
                'url': f'/thermal-rolls/{record.pk}/',
                'timestamp': record.timestamp,
                'status': None
            })
    
    # This week's activity
    week_ago = timezone.now() - timedelta(days=7)
    support_this_week = support_records.filter(timestamp__gte=week_ago).count()
    asset_this_week = asset_records.filter(timestamp__gte=week_ago).count()
    vendor_this_week = vendor_records.filter(timestamp__gte=week_ago).count()
    thermal_this_week = thermal_records.filter(timestamp__gte=week_ago).count()
    
    context = {
        # General
        'is_admin': is_admin,
        'today': timezone.now(),
        'total_count': total_count,
        
        # Total counts
        'support_count': support_count,
        'asset_count': asset_count,
        'vendor_count': vendor_count,
        'thermal_count': thermal_count,
        
        # Support Records status
        'support_pending': support_pending,
        'support_in_progress': support_in_progress,
        'support_solved': support_solved,
        
        # Asset Management status
        'asset_in_use': asset_in_use,
        'asset_returned': asset_returned,
        'asset_under_repair': asset_under_repair,
        
        # Vendor Assistance status
        'vendor_pending': vendor_pending,
        'vendor_ongoing': vendor_ongoing,
        'vendor_resolved': vendor_resolved,
        
        # Recent activity
        'recent_activity': recent_activity,
        
        # This week's activity
        'support_this_week': support_this_week,
        'asset_this_week': asset_this_week,
        'vendor_this_week': vendor_this_week,
        'thermal_this_week': thermal_this_week,
    }
    
    return render(request, 'dashboard.html', context)

