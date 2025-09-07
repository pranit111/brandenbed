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

from maintenance.forms import MaintenanceRequestForm
from maintenance.models import MaintenanceRequest
# ================================
# MAINTENANCE VIEWS
# ================================

@login_required
@user_passes_test(lambda u: u.user_type == 'employee')
def maintenance_request_create_view(request):
    """Create maintenance request"""
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            
            # Generate request ID
            last_request = MaintenanceRequest.objects.order_by('id').last()
            if last_request:
                request_id = f"MAINT{last_request.id + 1:05d}"
            else:
                request_id = "MAINT00001"
            maintenance_request.request_id = request_id
            maintenance_request.requested_by = request.user.employee
            maintenance_request.save()
            
            messages.success(request, 'Maintenance request created successfully!')
            return redirect('maintenance_request_detail', request_id=maintenance_request.id)
    else:
        form = MaintenanceRequestForm()
    
    return render(request, 'maintenance/request_form.html', {'form': form, 'action': 'Create'})
