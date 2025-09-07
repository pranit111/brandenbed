# core/views.py
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings


from leads.forms import ContactUsForm, LandlordPartnershipForm
from leads.models import Lead
from properties.models import Room
from support.models import SupportTicket
from .forms import ContactForm
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

import json


class HomeView(TemplateView):
    template_name = 'core/home.html'
    

class PropertiesView(TemplateView):
    template_name = 'core/properties.html'


class ServicesView(TemplateView):
    template_name = 'core/services.html'
    


class AboutView(TemplateView):
    template_name = 'core/about.html'
    

# Public Forms
class ContactView(CreateView):
    model = Lead
    form_class = ContactUsForm
    template_name = 'core/contact.html'
    success_url = '/leads/contact/thank-you/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Thank you for contacting us! We will get back to you within 24 hours.')
        return super().form_valid(form)

class LandlordsView(CreateView):
    model = Lead
    form_class = LandlordPartnershipForm
    template_name = 'core/landlords.html'
    success_url = '/leads/landlords/thank-you/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Thank you for your interest in partnering with us! Our team will review your property and contact you soon.')
        return super().form_valid(form)

    
    
    

# ================================
# API VIEWS (for AJAX calls)
# ================================

@login_required
def get_rooms_by_property(request):
    """API endpoint to get rooms for a property"""
    property_id = request.GET.get('property_id')
    rooms = Room.objects.filter(property_id=property_id).values('id', 'room_number', 'room_type')
    return JsonResponse({'rooms': list(rooms)})

@login_required
def quick_status_update(request):
    """API endpoint for quick status updates"""
    if request.method == 'POST':
        data = json.loads(request.body)
        model_type = data.get('model_type')
        object_id = data.get('object_id')
        new_status = data.get('status')
        
        # Handle different model types
        if model_type == 'lead':
            obj = get_object_or_404(Lead, id=object_id)
            obj.status = new_status
            obj.save()
        elif model_type == 'ticket':
            obj = get_object_or_404(SupportTicket, id=object_id)
            obj.status = new_status
            obj.save()
        # Add more model types as needed
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
