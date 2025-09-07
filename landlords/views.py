# landlords/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import csv

from .models import Landlord, LandlordDocument
from .forms import LandlordForm, LandlordDocumentForm, LandlordFilterForm, PartnershipUpdateForm
from properties.models import Property
from employees.models import Employee
from django.contrib.auth.models import User

from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from datetime import datetime
import logging
from .models import Landlord
from .forms import LandlordForm

logger = logging.getLogger(__name__)



class LandlordDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view showing landlord statistics and overview"""
    template_name = 'landlords/dashboard.html'
    context_object_name = 'landlords'
    
    def get_queryset(self):
        return Landlord.objects.select_related('user', 'assigned_bd_executive__user').order_by('-created_at')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        total_landlords = Landlord.objects.count()
        active_partners = Landlord.objects.filter(partnership_status='active').count()
        prospects = Landlord.objects.filter(partnership_status='prospect').count()
        under_evaluation = Landlord.objects.filter(partnership_status='under_evaluation').count()
        
        # Partnership status distribution
        partnership_stats = Landlord.objects.values('partnership_status').annotate(
            count=Count('id')
        ).order_by('partnership_status')
        
        # Landlord type distribution
        type_stats = Landlord.objects.values('landlord_type').annotate(
            count=Count('id')
        ).order_by('landlord_type')
        
        # Recent partnerships (last 30 days)
        recent_partnerships = Landlord.objects.filter(
            partnership_start_date__gte=timezone.now() - timedelta(days=30),
            partnership_status='active'
        ).count()
        
        # Total properties and earnings
        total_properties = Property.objects.filter(landlord__isnull=False).count()
        total_earnings = Landlord.objects.aggregate(
            total=Sum('total_earnings_to_date')
        )['total'] or 0
        
        context.update({
            'total_landlords': total_landlords,
            'active_partners': active_partners,
            'prospects': prospects,
            'under_evaluation': under_evaluation,
            'partnership_stats': partnership_stats,
            'type_stats': type_stats,
            'recent_partnerships': recent_partnerships,
            'total_properties': total_properties,
            'total_earnings': total_earnings,
            'recent_landlords': self.get_queryset(),
        })
        
        return context

class LandlordListView(LoginRequiredMixin, ListView):
    """List view for all landlords with filtering"""
    model = Landlord
    template_name = 'landlords/landlord_list.html'
    context_object_name = 'landlords'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Landlord.objects.select_related(
            'user', 'assigned_bd_executive__user'
        ).prefetch_related('properties').order_by('-created_at')
        
        # Apply filters
        form = LandlordFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['partnership_status']:
                queryset = queryset.filter(
                    partnership_status=form.cleaned_data['partnership_status']
                )
            
            if form.cleaned_data['landlord_type']:
                queryset = queryset.filter(
                    landlord_type=form.cleaned_data['landlord_type']
                )
            
            if form.cleaned_data['assigned_bd_executive']:
                queryset = queryset.filter(
                    assigned_bd_executive=form.cleaned_data['assigned_bd_executive']
                )
            
            if form.cleaned_data['search']:
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(landlord_id__icontains=search_term) |
                    Q(user__first_name__icontains=search_term) |
                    Q(user__last_name__icontains=search_term) |
                    Q(user__email__icontains=search_term) |
                    Q(company_name__icontains=search_term)
                )
            
            if form.cleaned_data['has_properties']:
                if form.cleaned_data['has_properties'] == 'yes':
                    queryset = queryset.filter(total_properties__gt=0)
                else:
                    queryset = queryset.filter(total_properties=0)
            
            if form.cleaned_data['partnership_date_from']:
                queryset = queryset.filter(
                    partnership_start_date__gte=form.cleaned_data['partnership_date_from']
                )
            
            if form.cleaned_data['partnership_date_to']:
                queryset = queryset.filter(
                    partnership_start_date__lte=form.cleaned_data['partnership_date_to']
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = LandlordFilterForm(self.request.GET)
        context['query_string'] = self.request.GET.urlencode()
        
        # Add summary statistics for current filter
        filtered_queryset = self.get_queryset()
        context['filtered_count'] = filtered_queryset.count()
        context['active_count'] = filtered_queryset.filter(partnership_status='active').count()
        
        return context

class LandlordDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a landlord"""
    model = Landlord
    template_name = 'landlords/landlord_detail.html'
    context_object_name = 'landlord'
    
    def get_object(self):
        return get_object_or_404(
            Landlord.objects.select_related(
                'user', 'assigned_bd_executive__user'
            ).prefetch_related(
                'properties', 'documents'
            ),
            landlord_id=self.kwargs['landlord_id']
        )
    
    def get_context_data(self, **kwargs):
        from django.db.models import Avg
        from django.utils import timezone
        
        context = super().get_context_data(**kwargs)
        landlord = self.object
        
        # Get landlord's properties - check if properties relation exists
        try:
            properties = landlord.properties.all().order_by('-created_at')
            context['properties'] = properties
        except AttributeError:
            # If properties relation doesn't exist, create empty queryset
            from properties.models import Property  # Adjust import based on your app structure
            properties = Property.objects.none()
            context['properties'] = properties
        
        # Performance metrics
        context['performance_metrics'] = {
            'total_properties': properties.count(),
            'active_properties': properties.filter(status='active').count() if properties.exists() else 0,
            'total_rooms': sum(prop.total_rooms or 0 for prop in properties),
            'avg_rent': properties.aggregate(avg_rent=Avg('expected_monthly_rent'))['avg_rent'] or 0,
        }
        
        # Partnership timeline
        context['partnership_duration'] = None
        if landlord.partnership_start_date:
            context['partnership_duration'] = (timezone.now().date() - landlord.partnership_start_date).days
        
        return context

class LandlordCreateView(LoginRequiredMixin, CreateView):
    """Create a new landlord"""
    model = Landlord
    form_class = LandlordForm
    template_name = 'landlords/landlord_create.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Generate unique landlord ID
                form.instance.landlord_id = self.generate_landlord_id()
                
                # Set default BD executive if not assigned
                if not form.instance.assigned_bd_executive:
                    # Try to assign to user creating the landlord if they're an employee
                    if hasattr(self.request.user, 'employee'):
                        form.instance.assigned_bd_executive = self.request.user.employee
                
                # Save the landlord (which also saves the user)
                response = super().form_valid(form)
                
                messages.success(
                    self.request, 
                    f'Landlord {self.object.landlord_id} created successfully!'
                )
                return response
                
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error creating landlord: {str(e)}", exc_info=True)
            
            # Add error message
            messages.error(
                self.request,
                f'Error creating landlord: {str(e)}. Please check the form data and try again.'
            )
            
            # Return to form with errors
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Add debug information
        messages.error(
            self.request,
            'Please correct the errors below. If the problem persists, contact support.'
        )
        logger.error(f"Form validation errors: {form.errors}")
        return super().form_invalid(form)

    def generate_landlord_id(self):
        """Generate unique landlord ID"""
        today = datetime.now()
        prefix = f"LL{today.year}{today.month:02d}"
        
        # Find the last landlord ID for this month
        last_landlord = Landlord.objects.filter(
            landlord_id__startswith=prefix
        ).order_by('landlord_id').last()
        
        if last_landlord:
            try:
                last_number = int(last_landlord.landlord_id[-4:])
                next_number = last_number + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1
        
        return f"{prefix}{next_number:04d}"

    def get_success_url(self):
        return reverse('landlords:landlord_detail', kwargs={'landlord_id': self.object.landlord_id})

    
    
class LandlordUpdateView(LoginRequiredMixin, UpdateView):
    """Update landlord information"""
    model = Landlord
    form_class = LandlordForm
    template_name = 'landlords/landlord_update.html'
    
    def get_object(self):
        return get_object_or_404(Landlord, landlord_id=self.kwargs['landlord_id'])
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Landlord information updated successfully!')
        return response
    
    def get_success_url(self):
        return reverse('landlords:landlord_detail', kwargs={'landlord_id': self.object.landlord_id})

@login_required
def update_partnership_status(request, landlord_id):
    """Update landlord partnership status"""
    landlord = get_object_or_404(Landlord, landlord_id=landlord_id)
    
    if request.method == 'POST':
        form = PartnershipUpdateForm(request.POST, instance=landlord)
        if form.is_valid():
            old_status = landlord.partnership_status
            updated_landlord = form.save()
            
            # Set partnership start date if status changed to active
            if (old_status != 'active' and updated_landlord.partnership_status == 'active' 
                and not updated_landlord.partnership_start_date):
                updated_landlord.partnership_start_date = timezone.now().date()
                updated_landlord.save()
            
            # Create activity log (if you have one)
            # ActivityLog.objects.create(...)
            
            messages.success(
                request, 
                f'Partnership status updated from {old_status} to {updated_landlord.partnership_status}'
            )
        else:
            messages.error(request, 'Error updating partnership status')
    
    return redirect('landlords:landlord_detail', landlord_id=landlord_id)

@login_required
def upload_document(request, landlord_id):
    """Upload document for a landlord"""
    landlord = get_object_or_404(Landlord, landlord_id=landlord_id)
    
    if request.method == 'POST':
        form = LandlordDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.landlord = landlord
            document.uploaded_by = request.user.employee
            document.save()
            
            messages.success(request, 'Document uploaded successfully!')
        else:
            messages.error(request, 'Error uploading document. Please check the form.')
    
    return redirect('landlords:landlord_detail', landlord_id=landlord_id)

@login_required
def delete_document(request, landlord_id, document_id):
    """Delete a landlord document"""
    landlord = get_object_or_404(Landlord, landlord_id=landlord_id)
    document = get_object_or_404(LandlordDocument, id=document_id, landlord=landlord)
    
    if request.method == 'POST':
        document_title = document.title
        document.delete()
        messages.success(request, f'Document "{document_title}" deleted successfully!')
    
    return redirect('landlords:landlord_detail', landlord_id=landlord_id)

class ProspectsView(LoginRequiredMixin, ListView):
    """View for landlord prospects"""
    template_name = 'landlords/prospects.html'
    context_object_name = 'prospects'
    paginate_by = 20
    
    def get_queryset(self):
        return Landlord.objects.filter(
            partnership_status__in=['prospect', 'under_evaluation']
        ).select_related(
            'user', 'assigned_bd_executive__user'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Prospect statistics
        context['total_prospects'] = self.get_queryset().count()
        context['new_this_month'] = self.get_queryset().filter(
            created_at__gte=timezone.now().replace(day=1)
        ).count()
        
        return context

@login_required
def landlord_stats_api(request):
    """API endpoint for landlord statistics (for AJAX/charts)"""
    
    # Monthly registration trends
    from django.db.models.functions import TruncMonth
    
    monthly_data = Landlord.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Partnership status distribution
    status_data = Landlord.objects.values('partnership_status').annotate(
        count=Count('id')
    ).order_by('partnership_status')
    
    # Landlord type distribution
    type_data = Landlord.objects.values('landlord_type').annotate(
        count=Count('id')
    ).order_by('landlord_type')
    
    # Properties per landlord
    properties_data = Landlord.objects.values('total_properties').annotate(
        count=Count('id')
    ).order_by('total_properties')
    
    return JsonResponse({
        'monthly_trends': list(monthly_data),
        'status_distribution': list(status_data),
        'type_distribution': list(type_data),
        'properties_distribution': list(properties_data),
    })

@login_required
def export_landlords(request):
    """Export landlords to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="landlords.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Landlord ID', 'Name', 'Email', 'Company', 'Type', 
        'Partnership Status', 'BD Executive', 'Total Properties', 
        'Total Earnings', 'Partnership Date', 'Created Date'
    ])
    
    landlords = Landlord.objects.select_related(
        'user', 'assigned_bd_executive__user'
    ).all()
    
    for landlord in landlords:
        writer.writerow([
            landlord.landlord_id,
            landlord.user.get_full_name(),
            landlord.user.email,
            landlord.company_name,
            landlord.get_landlord_type_display(),
            landlord.get_partnership_status_display(),
            landlord.assigned_bd_executive.user.get_full_name() if landlord.assigned_bd_executive else '',
            landlord.total_properties,
            landlord.total_earnings_to_date,
            landlord.partnership_start_date.strftime('%Y-%m-%d') if landlord.partnership_start_date else '',
            landlord.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response

@login_required
def bulk_assign_bd_executive(request):
    """Bulk assign BD executive to landlords"""
    if request.method == 'POST':
        landlord_ids = request.POST.getlist('landlord_ids')
        bd_executive_id = request.POST.get('bd_executive_id')
        
        if landlord_ids and bd_executive_id:
            bd_executive = get_object_or_404(Employee, id=bd_executive_id)
            
            landlords = Landlord.objects.filter(id__in=landlord_ids)
            updated_count = landlords.update(assigned_bd_executive=bd_executive)
            
            messages.success(
                request, 
                f'{updated_count} landlords assigned to {bd_executive.user.get_full_name()}'
            )
        else:
            messages.error(request, 'Please select landlords and a BD executive')
    
    return redirect('landlords:landlord_list')

@login_required
def performance_report(request, landlord_id):
    """Generate performance report for a landlord"""
    landlord = get_object_or_404(Landlord, landlord_id=landlord_id)
    
    # Calculate performance metrics
    properties = landlord.properties.all()
    total_rooms = sum(prop.total_rooms or 0 for prop in properties)
    occupied_rooms = sum(prop.occupied_rooms or 0 for prop in properties)
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Monthly revenue trends (last 12 months)
    # This would need to be implemented based on your rental/payment models
    
    context = {
        'landlord': landlord,
        'properties': properties,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'report_date': timezone.now().date(),
    }
    
    return render(request, 'landlords/performance_report.html', context)

class DocumentListView(LoginRequiredMixin, ListView):
    """List all documents for a landlord"""
    template_name = 'landlords/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        self.landlord = get_object_or_404(Landlord, landlord_id=self.kwargs['landlord_id'])
        return LandlordDocument.objects.filter(
            landlord=self.landlord
        ).select_related('uploaded_by__user').order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['landlord'] = self.landlord
        context['upload_form'] = LandlordDocumentForm()
        return context