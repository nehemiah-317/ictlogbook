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
    """Main dashboard view"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    from django.utils import timezone
    from support_records.models import SupportRecord
    from asset_management.models import AssetRecord
    from vendor_assistance.models import VendorAssistance
    from thermal_rolls.models import ThermalRollRecord
    
    # Get counts based on user role
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    if is_admin:
        # Admin sees all records
        support_count = SupportRecord.objects.count()
        asset_count = AssetRecord.objects.count()
        vendor_count = VendorAssistance.objects.count()
        thermal_count = ThermalRollRecord.objects.count()
    else:
        # Staff sees only their records
        support_count = SupportRecord.objects.filter(recorded_by=request.user).count()
        asset_count = AssetRecord.objects.filter(recorded_by=request.user).count()
        vendor_count = VendorAssistance.objects.filter(resolved_by=request.user).count()
        thermal_count = ThermalRollRecord.objects.filter(recorded_by=request.user).count()
    
    context = {
        'support_count': support_count,
        'asset_count': asset_count,
        'vendor_count': vendor_count,
        'thermal_count': thermal_count,
        'today': timezone.now(),
        'is_admin': is_admin,
    }
    
    return render(request, 'dashboard.html', context)

