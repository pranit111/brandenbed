# residents/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import csv

from .models import Resident, ResidencyContract
from .forms import ResidentApplicationForm, ContractForm
from accounts.models import User
from properties.models import Property, Room
from employees.models import Employee
from payments.models import Payment


@login_required
def resident_dashboard(request):
    """Main dashboard for resident management"""
    
    # Basic stats
    total_residents = Resident.objects.count()
    active_residents = Resident.objects.filter(status='active').count()
    new_applications = Resident.objects.filter(status='applied').count()
    pending_verification = Resident.objects.filter(status='verified', verification_completed=False).count()
    
    # Recent residents
    recent_residents = Resident.objects.select_related('user', 'current_property').order_by('-created_at')[:5]
    
    # Resident type distribution
    resident_types = Resident.objects.values('resident_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status distribution
    resident_statuses = Resident.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Contract expiry warnings (next 30 days)
    upcoming_expiry = ResidencyContract.objects.filter(
        end_date__lte=date.today() + timedelta(days=30),
        status='active'
    ).count()
    
    # Monthly income average
    avg_income = Resident.objects.filter(
        monthly_income__isnull=False
    ).aggregate(avg_income=Avg('monthly_income'))['avg_income'] or 0
    
    # Occupancy rate
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    context = {
        'total_residents': total_residents,
        'active_residents': active_residents,
        'new_applications': new_applications,
        'pending_verification': pending_verification,
        'recent_residents': recent_residents,
        'resident_types': resident_types,
        'resident_statuses': resident_statuses,
        'upcoming_expiry': upcoming_expiry,
        'avg_income': avg_income,
        'occupancy_rate': round(occupancy_rate, 1),
    }
    
    return render(request, 'residents/dashboard.html', context)


@login_required
def resident_list(request):
    """List all residents with filtering and searching"""
    
    residents = Resident.objects.select_related(
        'user', 'current_property', 'current_room', 'assigned_support_agent__user'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        residents = residents.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(resident_id__icontains=search_query) |
            Q(identification_number__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        residents = residents.filter(status=status_filter)
    
    # Filter by resident type
    type_filter = request.GET.get('type', '')
    if type_filter:
        residents = residents.filter(resident_type=type_filter)
    
    # Filter by property
    property_filter = request.GET.get('property', '')
    if property_filter:
        residents = residents.filter(current_property_id=property_filter)
    
    # Pagination
    paginator = Paginator(residents, 20)
    page = request.GET.get('page')
    residents = paginator.get_page(page)
    
    # Get filter options
    properties = Property.objects.all()
    status_choices = Resident.RESIDENT_STATUS_CHOICES
    type_choices = Resident.RESIDENT_TYPE_CHOICES
    
    context = {
        'residents': residents,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'property_filter': property_filter,
        'properties': properties,
        'status_choices': status_choices,
        'type_choices': type_choices,
    }
    
    return render(request, 'residents/resident_list.html', context)


@login_required
def resident_detail(request, resident_id):
    """Detailed view of a specific resident"""
    
    resident = get_object_or_404(
        Resident.objects.select_related(
            'user', 'current_property', 'current_room', 'assigned_support_agent__user'
        ),
        resident_id=resident_id
    )
    
    # Get contracts
    contracts = ResidencyContract.objects.filter(resident=resident).order_by('-created_at')
    active_contract = contracts.filter(status='active').first()
    
    # Get payments
    payments = Payment.objects.filter(
        resident=resident
    ).order_by('-created_at')[:10]
    
    # Payment stats
    total_payments = Payment.objects.filter(resident=resident).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    outstanding_payments = Payment.objects.filter(
        resident=resident,
        status='pending'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'resident': resident,
        'contracts': contracts,
        'active_contract': active_contract,
        'payments': payments,
        'total_payments': total_payments,
        'outstanding_payments': outstanding_payments,
    }
    
    return render(request, 'residents/resident_detail.html', context)


@login_required
def resident_create(request):
    """Create a new resident application"""
    
    if request.method == 'POST':
        form = ResidentApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user first
            user_data = {
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
                'email': request.POST.get('email', ''),
                'phone': request.POST.get('phone', ''),
                'nationality': request.POST.get('nationality', ''),
                'date_of_birth': request.POST.get('date_of_birth', ''),
                'gender': request.POST.get('gender', ''),
                'address': request.POST.get('address', ''),
                'city': request.POST.get('city', ''),
                'postal_code': request.POST.get('postal_code', ''),
                'country': request.POST.get('country', ''),
            }
            
            # Check if user already exists
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            
            if not created:
                # Check if resident already exists
                if Resident.objects.filter(user=user).exists():
                    messages.error(request, 'A resident with this email already exists.')
                    return render(request, 'residents/resident_create.html', {'form': form})
            
            # Create resident
            resident = form.save(commit=False)
            resident.user = user
            
            # Generate resident ID
            resident.resident_id = f"BB{timezone.now().strftime('%Y%m')}{Resident.objects.count() + 1:04d}"
            
            resident.save()
            
            messages.success(request, f'Resident application created successfully! ID: {resident.resident_id}')
            return redirect('residents:resident_detail', resident_id=resident.resident_id)
    else:
        form = ResidentApplicationForm()
    
    return render(request, 'residents/resident_create.html', {'form': form})


@login_required
def resident_edit(request, resident_id):
    """Edit existing resident"""
    
    resident = get_object_or_404(Resident, resident_id=resident_id)
    
    if request.method == 'POST':
        form = ResidentApplicationForm(request.POST, request.FILES, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resident information updated successfully!')
            return redirect('residents:resident_detail', resident_id=resident.resident_id)
    else:
        form = ResidentApplicationForm(instance=resident)
    
    context = {
        'form': form,
        'resident': resident,
        'is_edit': True,
    }
    
    return render(request, 'residents/resident_edit.html', context)


@login_required
def resident_delete(request, resident_id):
    """Delete resident (with confirmation)"""
    
    resident = get_object_or_404(Resident, resident_id=resident_id)
    
    if request.method == 'POST':
        resident_name = resident.user.get_full_name()
        resident.delete()
        messages.success(request, f'Resident {resident_name} deleted successfully!')
        return redirect('residents:resident_list')
    
    return render(request, 'residents/resident_delete_confirm.html', {'resident': resident})


# Contract Management Views

@login_required
def contract_list(request):
    """List all residency contracts"""
    
    contracts = ResidencyContract.objects.select_related(
        'resident__user', 'property_ref', 'room', 'created_by__user'
    ).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        contracts = contracts.filter(status=status_filter)
    
    # Filter by property
    property_filter = request.GET.get('property', '')
    if property_filter:
        contracts = contracts.filter(property_ref_id=property_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        contracts = contracts.filter(
            Q(contract_id__icontains=search_query) |
            Q(resident__user__first_name__icontains=search_query) |
            Q(resident__user__last_name__icontains=search_query) |
            Q(resident__resident_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(contracts, 20)
    page = request.GET.get('page')
    contracts = paginator.get_page(page)
    
    # Filter options
    properties = Property.objects.all()
    status_choices = ResidencyContract.CONTRACT_STATUS_CHOICES
    
    context = {
        'contracts': contracts,
        'search_query': search_query,
        'status_filter': status_filter,
        'property_filter': property_filter,
        'properties': properties,
        'status_choices': status_choices,
    }
    
    return render(request, 'residents/contract_list.html', context)


@login_required
def contract_create(request):
    """Create new residency contract"""
    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            
            # Generate contract ID
            contract.contract_id = f"CON{timezone.now().strftime('%Y%m')}{ResidencyContract.objects.count() + 1:04d}"
            
            # Set created by
            if hasattr(request.user, 'employee'):
                contract.created_by = request.user.employee
            
            contract.save()
            
            # Update resident status
            resident = contract.resident
            if resident.status == 'verified':
                resident.status = 'active'
                resident.current_property = contract.property_ref
                resident.current_room = contract.room
                resident.save()
            
            # Update room occupancy
            room = contract.room
            room.is_occupied = True
            room.current_resident = resident
            room.save()
            
            messages.success(request, f'Contract {contract.contract_id} created successfully!')
            return redirect('residents:contract_detail', contract_id=contract.contract_id)
    else:
        form = ContractForm()
        
        # Pre-fill resident if provided
        resident_id = request.GET.get('resident')
        if resident_id:
            try:
                resident = Resident.objects.get(resident_id=resident_id)
                form.fields['resident'].initial = resident.id
            except Resident.DoesNotExist:
                pass
    
    return render(request, 'residents/contract_create.html', {'form': form})


@login_required
def contract_detail(request, contract_id):
    """Detailed view of contract"""
    
    contract = get_object_or_404(
        ResidencyContract.objects.select_related(
            'resident__user', 'property_ref', 'room', 'created_by__user'
        ),
        contract_id=contract_id
    )
    
    # Get related payments
    payments = Payment.objects.filter(
        contract=contract
    ).order_by('-created_at')
    
    context = {
        'contract': contract,
        'payments': payments,
    }
    
    return render(request, 'residents/contract_detail.html', context)


@login_required
def update_resident_status(request, resident_id):
    """AJAX view to update resident status"""
    
    if request.method == 'POST':
        resident = get_object_or_404(Resident, resident_id=resident_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Resident.RESIDENT_STATUS_CHOICES):
            resident.status = new_status
            resident.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status updated to {resident.get_status_display()}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def resident_export(request):
    """Export residents to CSV"""
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="residents_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Resident ID', 'Name', 'Email', 'Phone', 'Type', 'Status',
        'University', 'Course', 'Current Property', 'Room',
        'Move In Date', 'Monthly Income', 'Created Date'
    ])
    
    residents = Resident.objects.select_related(
        'user', 'current_property', 'current_room'
    ).all()
    
    for resident in residents:
        writer.writerow([
            resident.resident_id,
            resident.user.get_full_name(),
            resident.user.email,
            resident.user.phone or '',
            resident.get_resident_type_display(),
            resident.get_status_display(),
            resident.university or '',
            resident.course or '',
            resident.current_property.name if resident.current_property else '',
            resident.current_room.room_number if resident.current_room else '',
            resident.move_in_date or '',
            resident.monthly_income or '',
            resident.created_at.strftime('%Y-%m-%d'),
        ])
    
    return response


@login_required
def resident_analytics(request):
    """Analytics dashboard for residents"""
    
    # Monthly registration trends (last 6 months)
    from django.db.models import Count, TruncMonth
    from dateutil.relativedelta import relativedelta
    
    six_months_ago = date.today() - relativedelta(months=6)
    monthly_registrations = Resident.objects.filter(
        created_at__date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Resident type breakdown
    type_breakdown = Resident.objects.values('resident_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status breakdown
    status_breakdown = Resident.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Average income by resident type
    income_by_type = Resident.objects.filter(
        monthly_income__isnull=False
    ).values('resident_type').annotate(
        avg_income=Avg('monthly_income'),
        count=Count('id')
    ).order_by('-avg_income')
    
    # Top universities
    top_universities = Resident.objects.filter(
        university__isnull=False
    ).exclude(university='').values('university').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'monthly_registrations': list(monthly_registrations),
        'type_breakdown': type_breakdown,
        'status_breakdown': status_breakdown,
        'income_by_type': income_by_type,
        'top_universities': top_universities,
    }
    
    return render(request, 'residents/analytics.html', context)