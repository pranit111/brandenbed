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

from landlords.models import Landlord
from payments.forms import PaymentForm
from payments.models import Payment
from residents.models import Resident

# ================================
# PAYMENT VIEWS
# ================================

@login_required
@user_passes_test(lambda u: u.user_type == 'employee')
def payment_create_view(request):
    """Create payment record"""
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            
            # Generate payment ID
            last_payment = Payment.objects.order_by('id').last()
            if last_payment:
                payment_id = f"PAY{last_payment.id + 1:06d}"
            else:
                payment_id = "PAY000001"
            payment.payment_id = payment_id
            payment.recorded_by = request.user.employee
            payment.save()
            
            messages.success(request, 'Payment recorded successfully!')
            return redirect('payment_detail', payment_id=payment.id)
    else:
        form = PaymentForm()
    
    return render(request, 'payments/payment_form.html', {'form': form, 'action': 'Create'})

@login_required
def payment_list_view(request):
    """List payments"""
    if request.user.user_type == 'resident':
        resident = get_object_or_404(Resident, user=request.user)
        payments = Payment.objects.filter(resident=resident).order_by('-transaction_date')
    elif request.user.user_type == 'landlord':
        landlord = get_object_or_404(Landlord, user=request.user)
        payments = Payment.objects.filter(landlord=landlord).order_by('-transaction_date')
    else:
        payments = Payment.objects.all().order_by('-transaction_date')
    
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'payments/payment_list.html', {
        'page_obj': page_obj,
        'payments': page_obj.object_list
    })
