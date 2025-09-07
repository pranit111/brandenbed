# employees/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Employee, Role
from .forms import EmployeeForm, RoleForm

User = get_user_model()

@login_required
def employee_list(request):
    """Display list of employees with filtering and pagination"""
    employees = Employee.objects.select_related('user', 'role', 'manager__user').all()
    
    # Apply filters
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    search_query = request.GET.get('search')
    
    if role_filter:
        employees = employees.filter(role__name=role_filter)
    
    if status_filter:
        employees = employees.filter(employment_status=status_filter)
    
    if type_filter:
        employees = employees.filter(employment_type=type_filter)
    
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Order by creation date (newest first)
    employees = employees.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get roles for filter dropdown
    roles = Role.objects.all()
    
    context = {
        'page_obj': page_obj,
        'employees': page_obj,
        'roles': roles,
        'current_filters': {
            'role': role_filter,
            'status': status_filter,
            'type': type_filter,
            'search': search_query,
        }
    }
    
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_detail(request, pk):
    """Display detailed view of an employee"""
    employee = get_object_or_404(Employee.objects.select_related('user', 'role', 'manager__user'), pk=pk)
    
    # Get team members if this employee is a manager
    team_members = None
    if employee.is_manager:
        team_members = Employee.objects.filter(manager=employee).select_related('user', 'role')
    
    context = {
        'employee': employee,
        'team_members': team_members,
    }
    
    return render(request, 'employees/employee_detail.html', context)

@login_required
def employee_create(request):
    """Create a new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                employee = form.save()
                messages.success(
                    request,
                    f'Employee {employee.user.get_full_name()} has been created successfully.'
                )

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Employee {employee.user.get_full_name()} created successfully.',
                        'redirect_url': reverse('employees:employee_detail', kwargs={'pk': employee.pk})
                    })

                return redirect('employees:employee_detail', pk=employee.pk)

            except Exception as e:
                messages.error(request, f'Error creating employee: {str(e)}')

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error creating employee: {str(e)}'
                    }, status=500)
        else:
            messages.error(request, 'Please correct the errors below.')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid form data',
                    'errors': form.errors
                }, status=400)

    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'employee': None,
        'title': 'Add New Employee'
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def role_list(request):
    """Display list of roles"""
    roles = Role.objects.annotate(
        employee_count=Count('employee')
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        roles = roles.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(roles, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'roles': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'employees/role_list.html', context)

@login_required
def role_detail(request, pk):
    """Display detailed view of a role"""
    role = get_object_or_404(Role, pk=pk)
    
    # Get employees with this role
    employees = Employee.objects.filter(role=role).select_related('user')
    
    context = {
        'role': role,
        'employees': employees,
    }
    
    return render(request, 'employees/role_detail.html', context)

@login_required
def role_create(request):
    """Create a new role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            try:
                role = form.save()
                messages.success(request, f'Role {role.get_name_display()} has been created successfully.')
                return redirect('employees:role_detail', pk=role.pk)
            except Exception as e:
                messages.error(request, f'Error creating role: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoleForm()
    
    context = {
        'form': form,
        'role': None,
        'title': 'Add New Role'
    }
    
    return render(request, 'employees/role_form.html', context)

@login_required
def role_edit(request, pk):
    """Edit an existing role"""
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            try:
                role = form.save()
                messages.success(request, f'Role {role.get_name_display()} has been updated successfully.')
                return redirect('employees:role_detail', pk=role.pk)
            except Exception as e:
                messages.error(request, f'Error updating role: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoleForm(instance=role)
    
    context = {
        'form': form,
        'role': role,
        'title': f'Edit {role.get_name_display()}'
    }
    
    return render(request, 'employees/role_form.html', context)

@login_required
@require_POST
def role_delete(request, pk):
    """Delete a role"""
    role = get_object_or_404(Role, pk=pk)
    
    # Check if role is in use
    employees_with_role = Employee.objects.filter(role=role).count()
    
    if employees_with_role > 0:
        messages.error(request, f'Cannot delete role "{role.get_name_display()}" as it is assigned to {employees_with_role} employee(s).')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': f'Cannot delete role as it is assigned to {employees_with_role} employee(s).'
            })
        
        return redirect('employees:role_detail', pk=pk)
    
    try:
        role_name = role.get_name_display()
        role.delete()
        messages.success(request, f'Role "{role_name}" has been deleted successfully.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Role "{role_name}" deleted successfully.'})
        
    except Exception as e:
        messages.error(request, f'Error deleting role: {str(e)}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Error deleting role: {str(e)}'})
    
    return redirect('employees:role_list')

@login_required
def employee_toggle_status(request, pk):
    """Toggle employee active/inactive status"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['active', 'inactive', 'on_leave', 'terminated']:
            employee.employment_status = new_status
            employee.save()
            
            messages.success(request, f'Employee status updated to {employee.get_employment_status_display()}.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'Status updated to {employee.get_employment_status_display()}',
                    'new_status': new_status,
                    'status_display': employee.get_employment_status_display()
                })
        else:
            messages.error(request, 'Invalid status provided.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid status provided.'})
    
    return redirect('employees:employee_detail', pk=pk)

@login_required
def role_permissions_preview(request, pk):
    """AJAX view to preview role permissions"""
    role = get_object_or_404(Role, pk=pk)
    
    permissions = {
        'core_management': {
            'can_manage_properties': role.can_manage_properties,
            'can_manage_landlords': role.can_manage_landlords,
            'can_manage_residents': role.can_manage_residents,
            'can_manage_employees': role.can_manage_employees,
        },
        'operations': {
            'can_handle_payments': role.can_handle_payments,
            'can_handle_maintenance': role.can_handle_maintenance,
            'can_handle_support_tickets': role.can_handle_support_tickets,
            'can_manage_housekeeping': role.can_manage_housekeeping,
        },
        'business_reports': {
            'can_manage_leads': role.can_manage_leads,
            'can_view_reports': role.can_view_reports,
            'can_access_crm': role.can_access_crm,
        }
    }
    
    return JsonResponse({
        'role_name': role.get_name_display(),
        'description': role.description,
        'permissions': permissions
    })

@login_required
def employee_hierarchy(request):
    """Display employee hierarchy/org chart"""
    # Get all employees with their managers
    employees = Employee.objects.select_related('user', 'role', 'manager__user').filter(
        employment_status='active'
    )
    
    # Build hierarchy structure
    managers = employees.filter(manager__isnull=True)
    
    context = {
        'managers': managers,
        'employees': employees,
    }
    
    return render(request, 'employees/employee_hierarchy.html', context)

@login_required
def employee_export(request):
    """Export employee data to CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="employees_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 
        'Role', 'Employment Type', 'Status', 'Manager', 'Hire Date',
        'Salary', 'Work Location', 'Skills'
    ])
    
    # Write employee data
    employees = Employee.objects.select_related('user', 'role', 'manager__user').all()
    
    for employee in employees:
        writer.writerow([
            employee.employee_id,
            employee.user.first_name,
            employee.user.last_name,
            employee.user.email,
            employee.user.phone_number or '',
            employee.role.get_name_display() if employee.role else '',
            employee.get_employment_type_display(),
            employee.get_employment_status_display(),
            employee.manager.user.get_full_name() if employee.manager else '',
            employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else '',
            employee.monthly_salary or '',
            employee.work_location or '',
            employee.skills or ''
        ])
    
    return response


@login_required
def employee_edit(request, pk):
    """Edit an existing employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            try:
                employee = form.save()
                messages.success(request, f'Employee {employee.user.get_full_name()} has been updated successfully.')
                return redirect('employees:employee_detail', pk=employee.pk)
            except Exception as e:
                messages.error(request, f'Error updating employee: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
        'title': f'Edit {employee.user.get_full_name()}'
    }
    
    return render(request, 'employees/employee_form.html', context)

@login_required
@require_POST
def employee_delete(request, pk):
    """Delete an employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    try:
        employee_name = employee.user.get_full_name()
        user = employee.user

        # Delete employee first, then user
        employee.delete()
        user.delete()

        messages.success(request, f'Employee {employee_name} has been deleted successfully.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Employee {employee_name} deleted successfully.'
            })

        return redirect('employees:list')  # adjust to your employee list view name

    except Exception as e:
        messages.error(request, f'Error deleting employee: {str(e)}')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting employee: {str(e)}'
            }, status=500)

        return redirect('employees:list')  # fallback for normal request
