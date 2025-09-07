# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import transaction
import json

from accounts.forms import UserUpdateForm
from accounts.models import User
from landlords.models import Landlord
from leads.models import Lead
from maintenance.models import MaintenanceRequest
from payments.models import Payment
from properties.models import Property
from residents.models import ResidencyContract, Resident
from support.models import SupportTicket
from employees.models import Employee, Role

# ================================
# DASHBOARD VIEWS
# ================================

@login_required
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    context = {}

    if user.user_type == 'employee':
        # Employee dashboard
        context.update({
            'total_properties': Property.objects.filter(status='active').count(),
            'total_residents': Resident.objects.filter(status='active').count(),
            'pending_tickets': SupportTicket.objects.filter(status__in=['open', 'in_progress']).count(),
            'new_leads': Lead.objects.filter(status='new').count(),
            'recent_tickets': SupportTicket.objects.filter(assigned_to__user=user).order_by('-created_at')[:5],
            'upcoming_tasks': MaintenanceRequest.objects.filter(
                assigned_employee__user=user, status='scheduled'
            ).order_by('scheduled_date')[:5]
        })
        return render(request, 'dashboards/employee_dashboard.html', context)

    elif user.user_type == 'landlord':
        # Landlord dashboard
        landlord = get_object_or_404(Landlord, user=user)
        context.update({
            'landlord': landlord,
            'my_properties': Property.objects.filter(landlord=landlord),
            'total_revenue': Payment.objects.filter(
                landlord=landlord, status='verified'
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
            'recent_payments': Payment.objects.filter(landlord=landlord).order_by('-transaction_date')[:5]
        })
        return render(request, 'dashboards/landlord_dashboard.html', context)

    elif user.user_type == 'resident':
        # Resident dashboard
        resident = get_object_or_404(Resident, user=user)
        context.update({
            'resident': resident,
            'current_contract': ResidencyContract.objects.filter(
                resident=resident, status='active'
            ).first(),
            'my_tickets': SupportTicket.objects.filter(resident=resident).order_by('-created_at')[:5],
            'upcoming_payments': Payment.objects.filter(
                resident=resident, status='pending'
            ).order_by('due_date')[:3]
        })
        return render(request, 'dashboards/resident_dashboard.html', context)

    elif user.is_superuser:
        # Admin dashboard
        context.update({
            'total_users': User.objects.count(),
            'total_properties': Property.objects.count(),
            'total_residents': Resident.objects.count(),
            'total_landlords': Landlord.objects.count(),
            'recent_logins': User.objects.order_by('-last_login')[:5],
        })
        return render(request, 'dashboards/admin_dashboard.html', context)

# ================================
# PROFILE VIEWS
# ================================

@login_required
def profile_view(request):
    """Profile view for all user types"""
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'employee':
        try:
            employee = Employee.objects.select_related('department', 'role', 'manager').get(user=user)
            context.update({
                'employee': employee,
                'subordinates': Employee.objects.filter(manager=employee),
            })
        except Employee.DoesNotExist:
            messages.warning(request, 'Employee profile not found. Please contact admin.')
        return render(request, 'profiles/employee_profile.html', context)
    
    elif user.user_type == 'landlord':
        try:
            landlord = Landlord.objects.select_related('assigned_bd_executive__user').get(user=user)
            context.update({
                'landlord': landlord,
                'properties': Property.objects.filter(landlord=landlord),
                'documents': landlord.documents.all().order_by('-uploaded_at')
            })
        except Landlord.DoesNotExist:
            messages.warning(request, 'Landlord profile not found. Please contact admin.')
        return render(request, 'profiles/landlord_profile.html', context)
    
    elif user.user_type == 'resident':
        try:
            resident = Resident.objects.select_related(
                'current_property', 'current_room', 'assigned_support_agent__user'
            ).get(user=user)
            current_contract = ResidencyContract.objects.filter(
                resident=resident, status='active'
            ).first()
            context.update({
                'resident': resident,
                'current_contract': current_contract,
                'contracts_history': ResidencyContract.objects.filter(resident=resident).order_by('-created_at')
            })
        except Resident.DoesNotExist:
            messages.warning(request, 'Resident profile not found. Please contact admin.')
        return render(request, 'profiles/resident_profile.html', context)
    
    elif user.is_superuser:
        # Admin profile
        context.update({
            'system_stats': {
                'total_users': User.objects.count(),
                'active_employees': Employee.objects.filter(employment_status='active').count(),
                'active_landlords': Landlord.objects.filter(partnership_status='active').count(),
                'active_residents': Resident.objects.filter(status='active').count(),
                'total_properties': Property.objects.count(),
            }
        })
        return render(request, 'profiles/admin_profile.html', context)



@login_required
def profile_edit_view(request):
    """Edit profile for all user types with all fields"""
    user = request.user
    
    if request.method == 'POST':
        # Handle basic user information update
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        
        if user_form.is_valid():
            user_form.save()
            
            # Handle role-specific updates
            if user.user_type == 'employee':
                try:
                    employee = Employee.objects.get(user=user)
                    employee.work_location = request.POST.get('work_location', employee.work_location)
                    employee.shift_timing = request.POST.get('shift_timing', employee.shift_timing)
                    employee.skills = request.POST.get('skills', employee.skills)
                    employee.certifications = request.POST.get('certifications', employee.certifications)
                    employee.notes = request.POST.get('employee_notes', employee.notes)
                    employee.save()
                except Employee.DoesNotExist:
                    pass
                    
            elif user.user_type == 'landlord':
                try:
                    landlord = Landlord.objects.get(user=user)
                    landlord.landlord_type = request.POST.get('landlord_type', landlord.landlord_type)
                    landlord.company_name = request.POST.get('company_name', landlord.company_name)
                    landlord.tax_id = request.POST.get('tax_id', landlord.tax_id)
                    landlord.preferred_communication = request.POST.get('preferred_communication', landlord.preferred_communication)
                    landlord.bank_name = request.POST.get('bank_name', landlord.bank_name)
                    landlord.bank_account_number = request.POST.get('bank_account_number', landlord.bank_account_number)
                    landlord.iban = request.POST.get('iban', landlord.iban)
                    landlord.preferred_payout_schedule = request.POST.get('preferred_payout_schedule', landlord.preferred_payout_schedule)
                    landlord.guaranteed_rent_preference = 'guaranteed_rent_preference' in request.POST
                    landlord.maintenance_handling = request.POST.get('maintenance_handling', landlord.maintenance_handling)
                    landlord.notes = request.POST.get('landlord_notes', landlord.notes)
                    landlord.save()
                except Landlord.DoesNotExist:
                    pass
                    
            elif user.user_type == 'resident':
                try:
                    resident = Resident.objects.get(user=user)
                    resident.resident_type = request.POST.get('resident_type', resident.resident_type)
                    resident.identification_type = request.POST.get('identification_type', resident.identification_type)
                    resident.identification_number = request.POST.get('identification_number', resident.identification_number)
                    resident.university = request.POST.get('university', resident.university)
                    resident.course = request.POST.get('course', resident.course)
                    resident.employer = request.POST.get('employer', resident.employer)
                    resident.job_title = request.POST.get('job_title', resident.job_title)
                    resident.monthly_income = request.POST.get('monthly_income', resident.monthly_income)
                    resident.income_source = request.POST.get('income_source', resident.income_source)
                    resident.visa_type = request.POST.get('visa_type', resident.visa_type)
                    
                    if request.POST.get('visa_expiry'):
                        resident.visa_expiry = request.POST.get('visa_expiry')
                    
                    resident.preferred_room_type = request.POST.get('preferred_room_type', resident.preferred_room_type)
                    resident.preferred_location = request.POST.get('preferred_location', resident.preferred_location)
                    resident.budget_range = request.POST.get('budget_range', resident.budget_range)
                    resident.parent_guardian_name = request.POST.get('parent_guardian_name', resident.parent_guardian_name)
                    resident.parent_guardian_phone = request.POST.get('parent_guardian_phone', resident.parent_guardian_phone)
                    resident.parent_guardian_email = request.POST.get('parent_guardian_email', resident.parent_guardian_email)
                    resident.dietary_requirements = request.POST.get('dietary_requirements', resident.dietary_requirements)
                    resident.medical_conditions = request.POST.get('medical_conditions', resident.medical_conditions)
                    resident.special_needs = request.POST.get('special_needs', resident.special_needs)
                    resident.notes = request.POST.get('resident_notes', resident.notes)
                    resident.save()
                except Resident.DoesNotExist:
                    pass
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    # GET request - show edit form
    context = {'user': user}
    
    if user.user_type == 'employee':
        try:
            employee = Employee.objects.get(user=user)
            context['employee'] = employee
        except Employee.DoesNotExist:
            pass
    elif user.user_type == 'landlord':
        try:
            landlord = Landlord.objects.get(user=user)
            context['landlord'] = landlord
        except Landlord.DoesNotExist:
            pass
    elif user.user_type == 'resident':
        try:
            resident = Resident.objects.get(user=user)
            context['resident'] = resident
        except Resident.DoesNotExist:
            pass
    
    return render(request, 'profiles/profile_edit.html', context)





@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('dashboard:profile')
    
    return render(request, 'profiles/change_password.html')

@login_required
def notification_settings_view(request):
    """Notification settings view"""
    user = request.user
    
    if request.method == 'POST':
        user.marketing_consent = 'marketing_consent' in request.POST
        user.whatsapp_consent = 'whatsapp_consent' in request.POST
        user.save()
        messages.success(request, 'Notification settings updated successfully!')
        return redirect('dashboard:profile')
    
    return render(request, 'profiles/notification_settings.html', {'user': user})