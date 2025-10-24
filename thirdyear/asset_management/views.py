from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import AssetRecord
from .forms import AssetRecordForm


def user_is_admin(user):
    """Check if user is in Admin group"""
    return user.groups.filter(name='Admin').exists()


@login_required
def asset_record_list(request):
    """List all asset records with filtering and search"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        records = AssetRecord.objects.all()
    else:
        records = AssetRecord.objects.filter(recorded_by=request.user)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(staff_name__icontains=search_query) |
            Q(staff_id__icontains=search_query) |
            Q(asset_type__icontains=search_query) |
            Q(division__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        records = records.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'is_admin': is_admin,
        'status_choices': AssetRecord.STATUS_CHOICES,
    }
    return render(request, 'asset_management/list.html', context)


@login_required
def asset_record_detail(request, pk):
    """View details of a specific asset record"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        record = get_object_or_404(AssetRecord, pk=pk)
    else:
        record = get_object_or_404(AssetRecord, pk=pk, recorded_by=request.user)
    
    context = {
        'record': record,
        'is_admin': is_admin,
    }
    return render(request, 'asset_management/detail.html', context)


@login_required
def asset_record_create(request):
    """Create a new asset record"""
    if request.method == 'POST':
        form = AssetRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, 'Asset record created successfully!')
            return redirect('asset_management:detail', pk=record.pk)
    else:
        form = AssetRecordForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'asset_management/form.html', context)


@login_required
def asset_record_update(request, pk):
    """Update an existing asset record"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        record = get_object_or_404(AssetRecord, pk=pk)
    else:
        record = get_object_or_404(AssetRecord, pk=pk, recorded_by=request.user)
    
    if request.method == 'POST':
        form = AssetRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset record updated successfully!')
            return redirect('asset_management:detail', pk=record.pk)
    else:
        form = AssetRecordForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
        'action': 'Update',
    }
    return render(request, 'asset_management/form.html', context)


@login_required
def asset_record_delete(request, pk):
    """Delete an asset record (Admin only)"""
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('asset_management:list')
    
    record = get_object_or_404(AssetRecord, pk=pk)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Asset record deleted successfully!')
        return redirect('asset_management:list')
    
    context = {
        'record': record,
    }
    return render(request, 'asset_management/delete_confirm.html', context)

