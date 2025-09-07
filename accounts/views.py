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

from accounts.forms import CustomLoginForm, CustomUserRegistrationForm

# ================================
# AUTHENTICATION VIEWS
# ================================

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            
            # Create specific profile based on user type
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'landlord':
                return redirect('landlord_profile_setup')
            elif user_type == 'resident':
                return redirect('resident_application')
            else:
                return redirect('dashboard')
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# views.py
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta

def login_view(request):
    """Custom login view with remember me functionality"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiration based on "remember me" choice
                if remember_me:
                    # Set session to expire in 2 weeks
                    request.session.set_expiry(1209600)  # 2 weeks in seconds
                else:
                    # Session expires when browser closes
                    request.session.set_expiry(0)
                
                # Update last login time
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                
                next_url = request.GET.get('next', 'dashboard:dashboard')
                return redirect(next_url)
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})