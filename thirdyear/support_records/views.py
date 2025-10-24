from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import SupportRecord
from .forms import SupportRecordForm


def user_is_admin(user):
    """Check if user is in Admin group"""
    return user.groups.filter(name='Admin').exists()


@login_required
def support_record_list(request):
    """List all support records with filtering and search"""
    is_admin = user_is_admin(request.user)
    
    # Base queryset - admin sees all, staff sees only theirs
    if is_admin:
        records = SupportRecord.objects.all()
    else:
        records = SupportRecord.objects.filter(recorded_by=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(staff_name__icontains=search_query) |
            Q(staff_id__icontains=search_query) |
            Q(issue_reported__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        records = records.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(records, 10)  # 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'is_admin': is_admin,
        'status_choices': SupportRecord.STATUS_CHOICES,
    }
    return render(request, 'support_records/list.html', context)


@login_required
def support_record_detail(request, pk):
    """View details of a specific support record"""
    is_admin = user_is_admin(request.user)
    
    # Get the record
    if is_admin:
        record = get_object_or_404(SupportRecord, pk=pk)
    else:
        # Non-admin can only view their own records
        record = get_object_or_404(SupportRecord, pk=pk, recorded_by=request.user)
    
    context = {
        'record': record,
        'is_admin': is_admin,
    }
    return render(request, 'support_records/detail.html', context)


@login_required
def support_record_create(request):
    """Create a new support record"""
    if request.method == 'POST':
        form = SupportRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, 'Support record created successfully!')
            return redirect('support_records:detail', pk=record.pk)
    else:
        form = SupportRecordForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'support_records/form.html', context)


@login_required
def support_record_update(request, pk):
    """Update an existing support record"""
    is_admin = user_is_admin(request.user)
    
    # Get the record - admin can edit all, staff only theirs
    if is_admin:
        record = get_object_or_404(SupportRecord, pk=pk)
    else:
        record = get_object_or_404(SupportRecord, pk=pk, recorded_by=request.user)
    
    if request.method == 'POST':
        form = SupportRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Support record updated successfully!')
            return redirect('support_records:detail', pk=record.pk)
    else:
        form = SupportRecordForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
        'action': 'Update',
    }
    return render(request, 'support_records/form.html', context)


@login_required
def support_record_delete(request, pk):
    """Delete a support record (Admin only)"""
    if not user_is_admin(request.user):
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('support_records:list')
    
    record = get_object_or_404(SupportRecord, pk=pk)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Support record deleted successfully!')
        return redirect('support_records:list')
    
    context = {
        'record': record,
    }
    return render(request, 'support_records/delete_confirm.html', context)

