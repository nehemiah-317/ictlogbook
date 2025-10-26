from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import VendorAssistance
from .forms import VendorAssistanceForm


def user_is_admin(user):
    """Check if user is in Admin group"""
    return user.groups.filter(name='Admin').exists()


@login_required
def vendor_assistance_list(request):
    """List all vendor assistance records with filtering and search"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        records = VendorAssistance.objects.all()
    else:
        records = VendorAssistance.objects.filter(resolved_by=request.user)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        records = records.filter(
            Q(company_name__icontains=search_query) |
            Q(cashier_owner_name__icontains=search_query) |
            Q(problem_reported__icontains=search_query)
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
        'records': records,  # For compatibility with templates
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'is_admin': is_admin,
        'status_choices': VendorAssistance.STATUS_CHOICES,
    }
    return render(request, 'vendor_assistance/list.html', context)


@login_required
def vendor_assistance_detail(request, pk):
    """View details of a specific vendor assistance record"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        record = get_object_or_404(VendorAssistance, pk=pk)
    else:
        record = get_object_or_404(VendorAssistance, pk=pk, resolved_by=request.user)
    
    context = {
        'record': record,
        'is_admin': is_admin,
    }
    return render(request, 'vendor_assistance/detail.html', context)


@login_required
def vendor_assistance_create(request):
    """Create a new vendor assistance record"""
    if request.method == 'POST':
        form = VendorAssistanceForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.resolved_by = request.user
            record.save()
            messages.success(request, 'Vendor assistance record created successfully!')
            return redirect('vendor_assistance:detail', pk=record.pk)
    else:
        form = VendorAssistanceForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'vendor_assistance/form.html', context)


@login_required
def vendor_assistance_update(request, pk):
    """Update an existing vendor assistance record"""
    is_admin = user_is_admin(request.user)
    
    if is_admin:
        record = get_object_or_404(VendorAssistance, pk=pk)
    else:
        record = get_object_or_404(VendorAssistance, pk=pk, resolved_by=request.user)
    
    if request.method == 'POST':
        form = VendorAssistanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor assistance record updated successfully!')
            return redirect('vendor_assistance:detail', pk=record.pk)
    else:
        form = VendorAssistanceForm(instance=record)
    
    context = {
        'form': form,
        'record': record,
        'action': 'Update',
    }
    return render(request, 'vendor_assistance/form.html', context)


@login_required
def vendor_assistance_delete(request, pk):
    """Delete a vendor assistance record (Admin only)"""
    is_admin = user_is_admin(request.user)
    
    if not is_admin:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('vendor_assistance:list')
    
    record = get_object_or_404(VendorAssistance, pk=pk)
    
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Vendor assistance record deleted successfully!')
        return redirect('vendor_assistance:list')
    
    context = {
        'record': record,
        'is_admin': is_admin,
    }
    return render(request, 'vendor_assistance/delete.html', context)

