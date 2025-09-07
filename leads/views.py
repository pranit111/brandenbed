# leads/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
from datetime import datetime, timedelta

from .models import Lead, LeadActivity, LeadSource
from .forms import (
    ContactUsForm, LandlordPartnershipForm, LeadManagementForm,
    LeadActivityForm, LeadFilterForm
)






def contact_thank_you(request):
    return render(request, 'leads/thank_you.html', {
        'title': 'Thank You!',
        'message': 'We have received your inquiry and will get back to you within 24 hours.',
        'type': 'contact'
    })


def landlord_thank_you(request):
    return render(request, 'leads/thank_you.html', {
        'title': 'Thank You!',
        'message': 'Thank you for your interest in partnering with BrandenBed. Our team will review your property details and contact you soon.',
        'type': 'landlord'
    })


# CRM Views (Login Required)
@login_required
def lead_dashboard(request):
    """Dashboard showing lead statistics and recent activities"""
    # Lead statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    converted_leads = Lead.objects.filter(is_converted=True).count()
    
    # Recent leads
    recent_leads = Lead.objects.select_related('assigned_to__user').order_by('-created_at')[:5]
    
    # Lead by type
    lead_types = Lead.objects.values('lead_type').annotate(count=Count('id'))
    
    # Lead by status
    lead_statuses = Lead.objects.values('status').annotate(count=Count('id'))
    
    # Leads requiring follow-up
    needs_followup = Lead.objects.filter(
        next_followup_date__lte=timezone.now(),
        status__in=['new', 'contacted', 'interested']
    ).count()
    
    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'converted_leads': converted_leads,
        'conversion_rate': round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0,
        'recent_leads': recent_leads,
        'lead_types': lead_types,
        'lead_statuses': lead_statuses,
        'needs_followup': needs_followup,
    }
    
    return render(request, 'leads/dashboard.html', context)


@login_required
def lead_list(request):
    """List all leads with filtering and pagination"""
    leads = Lead.objects.select_related('assigned_to__user').order_by('-created_at')
    
    # Apply filters
    filter_form = LeadFilterForm(request.GET)
    current_filters = {}
    
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('status'):
            leads = leads.filter(status=filter_form.cleaned_data['status'])
            current_filters['status'] = filter_form.cleaned_data['status']
        
        if filter_form.cleaned_data.get('lead_type'):
            leads = leads.filter(lead_type=filter_form.cleaned_data['lead_type'])
            current_filters['lead_type'] = filter_form.cleaned_data['lead_type']
        
        if filter_form.cleaned_data.get('priority'):
            leads = leads.filter(priority=filter_form.cleaned_data['priority'])
            current_filters['priority'] = filter_form.cleaned_data['priority']
        
        if filter_form.cleaned_data.get('search'):
            search_term = filter_form.cleaned_data['search']
            leads = leads.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(company_name__icontains=search_term)
            )
            current_filters['search'] = search_term
    
    # Pagination
    paginator = Paginator(leads, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'leads': page_obj,
        'page_obj': page_obj,
        'filter_form': filter_form,
        'current_filters': current_filters,
    }
    
    return render(request, 'leads/lead_list.html', context)


@login_required
def lead_detail(request, pk):
    """Detailed view of a single lead"""
    lead = get_object_or_404(Lead, pk=pk)
    activities = lead.activities.select_related('handled_by__user').order_by('-created_at')
    
    # Forms for updating lead
    if request.method == 'POST':
        if 'update_lead' in request.POST:
            form = LeadManagementForm(request.POST, instance=lead)
            if form.is_valid():
                form.save()
                messages.success(request, 'Lead updated successfully.')
                return redirect('leads:lead_detail', pk=lead.pk)
        
        elif 'add_activity' in request.POST:
            activity_form = LeadActivityForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.lead = lead
                activity.handled_by = request.user.employee if hasattr(request.user, 'employee') else None
                if activity.is_completed:
                    activity.completed_date = timezone.now()
                activity.save()
                
                # Update lead's last contact date
                lead.last_contact_date = timezone.now()
                lead.contact_attempts += 1
                lead.save()
                
                messages.success(request, 'Activity added successfully.')
                return redirect('leads:lead_detail', pk=lead.pk)
    
    else:
        form = LeadManagementForm(instance=lead)
        activity_form = LeadActivityForm()
    
    context = {
        'lead': lead,
        'activities': activities,
        'form': form,
        'activity_form': activity_form,
    }
    
    return render(request, 'leads/lead_detail.html', context)


@login_required
def lead_create(request):
    """Create a new lead manually"""
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = 'manual_entry'
            lead.save()
            messages.success(request, 'Lead created successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = ContactUsForm()
    
    return render(request, 'leads/lead_create.html', {'form': form})


@login_required
def lead_edit(request, pk):
    """Edit an existing lead"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        form = LeadManagementForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadManagementForm(instance=lead)
    
    return render(request, 'leads/lead_edit.html', {'form': form, 'lead': lead})


@login_required
@require_POST
def lead_delete(request, pk):
    """Delete a lead"""
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    messages.success(request, f'Lead "{lead.full_name}" deleted successfully.')
    return redirect('leads:lead_list')


@login_required
def lead_export(request):
    """Export leads to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Type', 'Name', 'Email', 'Phone', 'Company', 'Status',
        'Priority', 'Source', 'Created Date', 'Last Contact', 'Assigned To',
        'Property Address', 'Budget Range', 'Notes'
    ])
    
    for lead in Lead.objects.select_related('assigned_to__user'):
        writer.writerow([
            lead.id,
            lead.get_lead_type_display(),
            lead.full_name,
            lead.email,
            lead.phone_number,
            lead.company_name,
            lead.get_status_display(),
            lead.get_priority_display(),
            lead.get_source_display(),
            lead.created_at.strftime('%Y-%m-%d %H:%M'),
            lead.last_contact_date.strftime('%Y-%m-%d %H:%M') if lead.last_contact_date else '',
            lead.assigned_to.user.get_full_name() if lead.assigned_to else '',
            lead.property_address,
            lead.budget_range,
            lead.notes[:100] + '...' if len(lead.notes) > 100 else lead.notes
        ])
    
    return response


@login_required
@require_POST
def lead_bulk_action(request):
    """Handle bulk actions on leads"""
    action = request.POST.get('action')
    lead_ids = request.POST.getlist('lead_ids')
    
    if not lead_ids:
        messages.error(request, 'No leads selected.')
        return redirect('leads:lead_list')
    
    leads = Lead.objects.filter(id__in=lead_ids)
    
    if action == 'delete':
        count = leads.count()
        leads.delete()
        messages.success(request, f'{count} lead(s) deleted successfully.')
    
    elif action == 'assign':
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            from employees.models import Employee
            try:
                employee = Employee.objects.get(id=assigned_to_id)
                leads.update(assigned_to=employee)
                messages.success(request, f'{leads.count()} lead(s) assigned to {employee.user.get_full_name()}.')
            except Employee.DoesNotExist:
                messages.error(request, 'Invalid employee selected.')
    
    elif action == 'update_status':
        status = request.POST.get('status')
        if status in dict(Lead.LEAD_STATUS_CHOICES).keys():
            leads.update(status=status)
            messages.success(request, f'{leads.count()} lead(s) status updated.')
    
    return redirect('leads:lead_list')


@login_required
def activity_list(request):
    """List all activities across leads"""
    activities = LeadActivity.objects.select_related(
        'lead', 'handled_by__user'
    ).order_by('-created_at')
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        activities = activities.filter(created_at__date__gte=date_from)
    if date_to:
        activities = activities.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'leads/activity_list.html', {
        'activities': page_obj,
        'page_obj': page_obj,
    })


@login_required
def analytics(request):
    """Lead analytics and reports"""
    # Date range for analysis
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Basic metrics
    total_leads = Lead.objects.count()
    leads_this_month = Lead.objects.filter(created_at__date__gte=start_date).count()
    converted_leads = Lead.objects.filter(is_converted=True).count()
    
    # Lead sources performance
    source_performance = Lead.objects.values('source').annotate(
        total=Count('id'),
        converted=Count('id', filter=Q(is_converted=True))
    ).order_by('-total')
    
    # Monthly trend (last 6 months)
    monthly_data = []
    for i in range(6):
        month_start = (timezone.now().date() - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Lead.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_data.reverse()
    
    # Lead type distribution
    type_distribution = Lead.objects.values('lead_type').annotate(count=Count('id'))
    
    # Status distribution
    status_distribution = Lead.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'total_leads': total_leads,
        'leads_this_month': leads_this_month,
        'converted_leads': converted_leads,
        'conversion_rate': round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0,
        'source_performance': source_performance,
        'monthly_data': monthly_data,
        'type_distribution': type_distribution,
        'status_distribution': status_distribution,
    }
    
    return render(request, 'leads/analytics.html', context)


# API endpoints for AJAX calls
@login_required
def lead_quick_update(request, pk):
    """Quick update lead status via AJAX"""
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk)
        status = request.POST.get('status')
        
        if status in dict(Lead.LEAD_STATUS_CHOICES).keys():
            lead.status = status
            lead.save()
            
            # Create activity log
            LeadActivity.objects.create(
                lead=lead,
                activity_type='status_change',
                subject=f'Status changed to {lead.get_status_display()}',
                description=f'Status updated from admin interface',
                handled_by=request.user.employee if hasattr(request.user, 'employee') else None,
                is_completed=True,
                completed_date=timezone.now()
            )
            
            return JsonResponse({'success': True, 'status': lead.get_status_display()})
    
    return JsonResponse({'success': False})