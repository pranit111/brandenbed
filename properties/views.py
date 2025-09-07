
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

from accounts import forms
from core.forms import PropertySearchForm
from properties.forms import PropertyForm, RoomForm
from properties.models import Property, Room

# ================================
# PROPERTY VIEWS
# ================================

@login_required
def property_list_view(request):
    """List view for properties"""
    form = PropertySearchForm(request.GET)
    properties = Property.objects.all().select_related('landlord').order_by('-created_at')
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            properties = properties.filter(
                Q(name__icontains=search_query) |
                Q(address_line_1__icontains=search_query) |
                Q(district__icontains=search_query)
            )
        
        if form.cleaned_data.get('district'):
            properties = properties.filter(district__icontains=form.cleaned_data['district'])
        
        if form.cleaned_data.get('property_type'):
            properties = properties.filter(property_type=form.cleaned_data['property_type'])
        
        min_rent = form.cleaned_data.get('min_rent')
        max_rent = form.cleaned_data.get('max_rent')
        if min_rent:
            properties = properties.filter(expected_monthly_rent__gte=min_rent)
        if max_rent:
            properties = properties.filter(expected_monthly_rent__lte=max_rent)
    
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'properties/property_list.html', {
        'form': form,
        'page_obj': page_obj,
        'properties': page_obj.object_list
    })

@login_required
def property_detail_view(request, property_id):
    """Detail view for individual property"""
    property_obj = get_object_or_404(Property, id=property_id)
    rooms = Room.objects.filter(property_ref_id=property_obj)
    
    return render(request, 'properties/property_detail.html', {
        'property': property_obj,
        'rooms': rooms
    })

@login_required
def property_create_view(request):
    """Create new property"""
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_obj = form.save(commit=False)
            # Generate property ID
            last_property = Property.objects.order_by('id').last()
            if last_property:
                property_id = f"PROP{last_property.id + 1:04d}"
            else:
                property_id = "PROP0001"
            property_obj.property_id = property_id
            property_obj.save()
            messages.success(request, 'Property created successfully!')
            return redirect('properties:property_detail', property_id=property_obj.id)
    else:
        form = PropertyForm()
    
    return render(request, 'properties/property_form.html', {'form': form, 'action': 'Create'})

@login_required
def property_update_view(request, property_id):
    """Update existing property"""
    property_obj = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully!')
            return redirect('properties:property_detail', property_id=property_obj.id)
    else:
        form = PropertyForm(instance=property_obj)
    
    return render(request, 'properties/property_form.html', {
        'form': form, 
        'property': property_obj, 
        'action': 'Update'
    })



# ================================
# ROOM VIEWS
# ================================



# Room Views for Properties App
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import csv

from .models import Property, Room
from .forms import RoomForm


@login_required
def room_list_view(request, property_id):
    """List all rooms for a specific property with filtering and pagination"""
    property_obj = get_object_or_404(Property, id=property_id)
    rooms = Room.objects.filter(property_ref=property_obj).order_by('room_number')
    
    # Initialize filters dictionary
    current_filters = {
        'room_type': request.GET.get('room_type', ''),
        'status': request.GET.get('status', ''),
        'price_range': request.GET.get('price_range', ''),
        'search': request.GET.get('search', ''),
    }
    
    # Apply filters
    if current_filters['room_type']:
        rooms = rooms.filter(room_type=current_filters['room_type'])
    
    if current_filters['status']:
        rooms = rooms.filter(status=current_filters['status'])
    
    if current_filters['price_range']:
        if current_filters['price_range'] == '0-500':
            rooms = rooms.filter(monthly_rent__gte=0, monthly_rent__lte=500)
        elif current_filters['price_range'] == '500-800':
            rooms = rooms.filter(monthly_rent__gt=500, monthly_rent__lte=800)
        elif current_filters['price_range'] == '800-1200':
            rooms = rooms.filter(monthly_rent__gt=800, monthly_rent__lte=1200)
        elif current_filters['price_range'] == '1200+':
            rooms = rooms.filter(monthly_rent__gt=1200)
    
    if current_filters['search']:
        rooms = rooms.filter(
            Q(room_number__icontains=current_filters['search']) |
            Q(description__icontains=current_filters['search'])
        )
    
    # Get room statistics (before pagination)
    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='available').count()
    occupied_rooms = rooms.filter(status='occupied').count()
    
    # Calculate occupancy rate
    occupancy_rate = round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0)
    
    # Pagination
    paginator = Paginator(rooms, 20)  # Show 20 rooms per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'rooms/room_list.html', {
        'property': property_obj,
        'rooms': page_obj,
        'page_obj': page_obj,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'current_filters': current_filters,
    })


@login_required
def room_detail_view(request, property_id, room_id):
    """Display detailed information about a specific room"""
    property_obj = get_object_or_404(Property, id=property_id)
    room = get_object_or_404(Room, id=room_id, property_ref=property_obj)
    
    context = {
        'property': property_obj,
        'room': room,
    }
    
    return render(request, 'rooms/room_detail.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.views.decorators.http import require_http_methods
import logging

from properties.models import Property, Room
from properties.forms import PropertyForm, RoomForm

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET", "POST"])
def room_create_view(request, property_id):
    """Create a new room for a property"""
    property_obj = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, property_obj=property_obj)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create room instance but don't save to DB yet
                    room = form.save(commit=False)
                    
                    # Set the property reference
                    room.property_ref = property_obj
                    
                    # Ensure room number is properly formatted
                    if room.room_number:
                        room.room_number = room.room_number.strip().upper()
                    
                    # Set current_occupants to 0 for new rooms
                    room.current_occupants = 0
                    
                    # Save the room to database
                    room.save()
                    
                    messages.success(
                        request, 
                        f'Room {room.room_number} has been created successfully in {property_obj.name}.'
                    )
                    return redirect('properties:room_detail', property_id=property_obj.id, room_id=room.id)
                    
            except ValidationError as e:
                logger.warning(f"Validation error creating room: {e}")
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field, error)
                else:
                    form.add_error(None, str(e))
                messages.error(request, 'Please correct the errors below and try again.')
                    
            except Exception as e:
                logger.error(f"Unexpected error creating room: {e}", exc_info=True)
                messages.error(request, 'An unexpected error occurred while creating the room.')
                form.add_error(None, 'An unexpected error occurred. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        # GET request - create new form
        form = RoomForm(property_obj=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
        'is_edit': False,
        'page_title': f'Add New Room - {property_obj.name}',
    }
    
    return render(request, 'rooms/room_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def room_edit_view(request, property_id, room_id):
    """Edit an existing room"""
    property_obj = get_object_or_404(Property, id=property_id)
    room = get_object_or_404(Room, id=room_id, property_ref=property_obj)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room, property_obj=property_obj)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the form
                    room = form.save(commit=False)
                    
                    # Ensure property reference is maintained
                    room.property_ref = property_obj
                    
                    # Ensure room number is properly formatted
                    if room.room_number:
                        room.room_number = room.room_number.strip().upper()
                    
                    # Save to database
                    room.save()
                    
                    messages.success(
                        request, 
                        f'Room {room.room_number} has been updated successfully.'
                    )
                    return redirect('properties:room_detail', property_id=property_obj.id, room_id=room.id)
                    
            except ValidationError as e:
                logger.warning(f"Validation error updating room: {e}")
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field, error)
                else:
                    form.add_error(None, str(e))
                messages.error(request, 'Please correct the errors below and try again.')
                    
            except Exception as e:
                logger.error(f"Unexpected error updating room: {e}", exc_info=True)
                messages.error(request, 'An unexpected error occurred while updating the room.')
                form.add_error(None, 'An unexpected error occurred. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        # GET request - create form with existing instance
        form = RoomForm(instance=room, property_obj=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
        'room': room,
        'is_edit': True,
        'page_title': f'Edit Room {room.room_number} - {property_obj.name}',
    }
    
    return render(request, 'rooms/room_form.html', context)


# AJAX endpoints for dynamic validation
@login_required
def validate_room_number_ajax(request, property_id):
    """AJAX endpoint to validate room number uniqueness"""
    if request.method == 'GET':
        property_obj = get_object_or_404(Property, id=property_id)
        room_number = request.GET.get('room_number', '').strip().upper()
        room_id = request.GET.get('room_id', None)
        
        if not room_number:
            return JsonResponse({'valid': False, 'message': 'Room number is required'})
        
        existing_rooms = Room.objects.filter(
            property_ref=property_obj,
            room_number=room_number
        )
        
        if room_id:
            existing_rooms = existing_rooms.exclude(id=room_id)
        
        if existing_rooms.exists():
            return JsonResponse({
                'valid': False, 
                'message': f'Room number "{room_number}" already exists in this property'
            })
        
        return JsonResponse({'valid': True, 'message': 'Room number is available'})
    
    return JsonResponse({'valid': False, 'message': 'Invalid request method'})

@login_required
@require_POST
def room_delete_view(request, property_id, room_id):
    """Delete a room"""
    property_obj = get_object_or_404(Property, id=property_id)
    room = get_object_or_404(Room, id=room_id, property_ref=property_obj)
    
    room_number = room.room_number
    room.delete()
    messages.success(request, f'Room {room_number} has been deleted successfully.')
    return redirect('properties:room_list', property_id=property_id)


@login_required
def room_export_view(request, property_id):
    """Export rooms to CSV"""
    property_obj = get_object_or_404(Property, id=property_id)
    rooms = Room.objects.filter(property_ref=property_obj).order_by('room_number')
    
    # Apply the same filters as the list view if they exist
    room_type = request.GET.get('room_type')
    status = request.GET.get('status')
    price_range = request.GET.get('price_range')
    search = request.GET.get('search')
    
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if status:
        rooms = rooms.filter(status=status)
    if price_range:
        if price_range == '0-500':
            rooms = rooms.filter(monthly_rent__gte=0, monthly_rent__lte=500)
        elif price_range == '500-800':
            rooms = rooms.filter(monthly_rent__gt=500, monthly_rent__lte=800)
        elif price_range == '800-1200':
            rooms = rooms.filter(monthly_rent__gt=800, monthly_rent__lte=1200)
        elif price_range == '1200+':
            rooms = rooms.filter(monthly_rent__gt=1200)
    if search:
        rooms = rooms.filter(
            Q(room_number__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{property_obj.name}_rooms.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write CSV header
    writer.writerow([
        'Room Number',
        'Room Type',
        'Area (m²)',
        'Monthly Rent (€)',
        'Max Occupants',
        'Current Occupants',
        'Status',
        'Available From',
        'Min Contract Duration',
        'Max Contract Duration',
        'Has Private Bathroom',
        'Utilities Included',
        'Description'
    ])
    
    # Write room data
    for room in rooms:
        writer.writerow([
            room.room_number,
            room.get_room_type_display(),
            room.area,
            room.monthly_rent,
            room.max_occupants,
            room.current_occupants,
            room.get_status_display(),
            room.available_from.strftime('%Y-%m-%d') if room.available_from else '',
            room.min_contract_duration,
            room.max_contract_duration,
            'Yes' if room.has_private_bathroom else 'No',
            'Yes' if room.utilities_included else 'No',
            room.description or ''
        ])
    
    return response


@login_required
@require_POST
def room_update_status_view(request, property_id, room_id):
    """Update room status via AJAX or form submission"""
    property_obj = get_object_or_404(Property, id=property_id)
    room = get_object_or_404(Room, id=room_id, property_ref=property_obj)
    
    new_status = request.POST.get('status')
    if new_status and new_status in ['available', 'occupied', 'maintenance', 'reserved', 'blocked']:
        old_status = room.get_status_display()
        room.status = new_status
        room.save()
        messages.success(request, f'Room {room.room_number} status updated from {old_status} to {room.get_status_display()}.')
    else:
        messages.error(request, 'Invalid status provided.')
    
    return redirect('properties:room_detail', property_id=property_id, room_id=room_id)






