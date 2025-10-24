from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ThermalRollRecord
from .forms import ThermalRollRecordForm


def user_is_admin(user):
    """Check if user is in Admin group"""
    return user.groups.filter(name='Admin').exists()


@login_required
def thermal_roll_list(request):
    """List all thermal roll records with filtering and search"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        records = ThermalRollRecord.objects.all()
    else:
        records = ThermalRollRecord.objects.filter(recorded_by=request.user)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(vendor_name__icontains=search_query) |
            Q(cashier_owner_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'is_admin': is_admin,
    }
    return render(request, 'thermal_rolls/list.html', context)


@login_required
def thermal_roll_detail(request, pk):
    """View details of a specific thermal roll record"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        record = get_object_or_404(ThermalRollRecord, pk=pk)
    else:
        record = get_object_or_404(ThermalRollRecord, pk=pk, recorded_by=request.user)
    
    context = {
        'record': record,
        'is_admin': is_admin,
    }
    return render(request, 'thermal_rolls/detail.html', context)


@login_required
def thermal_roll_create(request):
    """Create a new thermal roll record"""
    if request.method == 'POST':
        form = ThermalRollRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, 'Thermal roll record created successfully!')
            return redirect('thermal_rolls:detail', pk=record.pk)
    else:
        form = ThermalRollRecordForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'thermal_rolls/form.html', context)


@login_required
def thermal_roll_update(request, pk):
    """Update an existing thermal roll record"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        record = get_object_or_404(ThermalRollRecord, pk=pk)
    else:
        record = get_object_or_404(ThermalRollRecord, pk=pk, recorded_by=request.user)
    
    if request.method == 'POST':
        form = ThermalRollRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thermal roll record updated successfully!')
            return redirect('thermal_rolls:detail', pk=record.pk)
    else:
        form = ThermalRollRecordForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
        'action': 'Update',
    }
    return render(request, 'thermal_rolls/form.html', context)


@login_required
def thermal_roll_delete(request, pk):
    """Delete a thermal roll record (Admin only)"""
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('thermal_rolls:list')
    
    record = get_object_or_404(ThermalRollRecord, pk=pk)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Thermal roll record deleted successfully!')
        return redirect('thermal_rolls:list')
    
    context = {
        'record': record,
    }
    return render(request, 'thermal_rolls/delete_confirm.html', context)

