# support/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.db import transaction
import uuid
from datetime import datetime, timedelta

from . import models

from .models import SupportTicket, SupportCategory, TicketComment
from .forms import SupportTicketForm, TicketCommentForm, TicketFilterForm, TicketUpdateForm
from residents.models import Resident
from employees.models import Employee

from django.contrib.auth import get_user_model
User = get_user_model()



class SupportDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view showing ticket statistics and overview"""
    template_name = 'support/dashboard.html'
    context_object_name = 'tickets'
    
    def get_queryset(self):
        return SupportTicket.objects.select_related(
            'resident__user', 'property_ref', 'category', 'assigned_to'
        ).prefetch_related('comments')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        total_tickets = SupportTicket.objects.count()
        open_tickets = SupportTicket.objects.filter(status='open').count()
        in_progress = SupportTicket.objects.filter(status='in_progress').count()
        overdue_tickets = SupportTicket.objects.filter(
            sla_due_date__lt=timezone.now(),
            status__in=['open', 'in_progress']
        ).count()
        
        # Recent tickets by category
        category_stats = SupportCategory.objects.annotate(
            ticket_count=Count('supportticket')
        ).order_by('-ticket_count')
        
        # Priority distribution
        priority_stats = SupportTicket.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        context.update({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'in_progress': in_progress,
            'overdue_tickets': overdue_tickets,
            'category_stats': category_stats,
            'priority_stats': priority_stats,
            'recent_tickets': self.get_queryset(),
        })
        
        return context

class TicketListView(LoginRequiredMixin, ListView):
    """List view for all support tickets with filtering"""
    model = SupportTicket
    template_name = 'support/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SupportTicket.objects.select_related(
            'resident__user', 'property_ref', 'category', 'assigned_to'
        ).order_by('priority', '-created_at')
        
        # Apply filters
        form = TicketFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['status']:
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            if form.cleaned_data['priority']:
                queryset = queryset.filter(priority=form.cleaned_data['priority'])
            
            if form.cleaned_data['category']:
                queryset = queryset.filter(category=form.cleaned_data['category'])
            
            if form.cleaned_data['assigned_to']:
                queryset = queryset.filter(assigned_to=form.cleaned_data['assigned_to'])
            
            if form.cleaned_data['search']:
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(ticket_id__icontains=search_term) |
                    Q(subject__icontains=search_term) |
                    Q(description__icontains=search_term) |
                    Q(resident__user__first_name__icontains=search_term) |
                    Q(resident__user__last_name__icontains=search_term)
                )
            
            if form.cleaned_data['overdue_only']:
                queryset = queryset.filter(
                    sla_due_date__lt=timezone.now(),
                    status__in=['open', 'in_progress']
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TicketFilterForm(self.request.GET)
        context['query_string'] = self.request.GET.urlencode()
        return context

class TicketDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a support ticket"""
    model = SupportTicket
    template_name = 'support/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_object(self):
        return get_object_or_404(
            SupportTicket.objects.select_related(
                'resident__user', 'property_ref', 'category', 'assigned_to', 'resolved_by'
            ).prefetch_related('comments__author__user'),
            ticket_id=self.kwargs['ticket_id']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TicketCommentForm()
        context['update_form'] = TicketUpdateForm(instance=self.object)
        
        # Get comments ordered by creation time
        context['comments'] = self.object.comments.select_related(
            'author__user'
        ).order_by('created_at')
        
        return context

class TicketCreateView(LoginRequiredMixin, CreateView):
    """Create a new support ticket"""
    model = SupportTicket
    form_class = SupportTicketForm
    template_name = 'support/ticket_create.html'
    
    def form_valid(self, form):
        # Generate unique ticket ID
        form.instance.ticket_id = self.generate_ticket_id()
        
        # Set SLA due date based on category
        if form.instance.category:
            form.instance.sla_due_date = timezone.now() + timedelta(
                hours=form.instance.category.sla_hours
            )
        
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Create initial comment
        if hasattr(self.request.user, 'employee'):
            TicketComment.objects.create(
            ticket=self.object,
            author=self.request.user.employee,
            comment_type='status_update',
            comment=f"Ticket created for: {self.object.subject}",
            is_internal=False
        )
        
        messages.success(
            self.request, 
            f'Support ticket {self.object.ticket_id} created successfully!'
        )
        return response
    
    def generate_ticket_id(self):
        """Generate unique ticket ID"""
        today = datetime.now()
        prefix = f"BB{today.year}{today.month:02d}"
        
        # Find the last ticket ID for this month
        last_ticket = SupportTicket.objects.filter(
            ticket_id__startswith=prefix
        ).order_by('ticket_id').last()
        
        if last_ticket:
            last_number = int(last_ticket.ticket_id[-4:])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f"{prefix}{next_number:04d}"
    
    def get_success_url(self):
        return reverse('support:ticket_detail', kwargs={'ticket_id': self.object.ticket_id})

@login_required
def ticket_update(request, ticket_id):
    """Update ticket status, priority, assignment, etc."""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            old_status = ticket.status
            old_assigned = ticket.assigned_to
            
            with transaction.atomic():
                updated_ticket = form.save()
                
                # Create status update comment
                changes = []
                if old_status != updated_ticket.status:
                    changes.append(f"Status: {old_status} → {updated_ticket.status}")
                
                if old_assigned != updated_ticket.assigned_to:
                    old_name = old_assigned.user.get_full_name() if old_assigned else "Unassigned"
                    new_name = updated_ticket.assigned_to.user.get_full_name() if updated_ticket.assigned_to else "Unassigned"
                    changes.append(f"Assigned: {old_name} → {new_name}")
                
                if changes:
                    TicketComment.objects.create(
                        ticket=updated_ticket,
                        author=request.user.employee,
                        comment_type='status_update',
                        comment=f"Ticket updated: {', '.join(changes)}",
                        is_internal=True
                    )
                
                # Mark first response time if this is the first update
                if not ticket.first_response_time and updated_ticket.status != 'open':
                    updated_ticket.first_response_time = timezone.now()
                    updated_ticket.save()
            
            messages.success(request, 'Ticket updated successfully!')
            return redirect('support:ticket_detail', ticket_id=ticket_id)
    
    return redirect('support:ticket_detail', ticket_id=ticket_id)

@login_required
def add_comment(request, ticket_id):
    """Add comment to a ticket"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user.employee
            comment.save()
            
            # Update ticket timestamp
            ticket.updated_at = timezone.now()
            ticket.save()
            
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment. Please check the form.')
    
    return redirect('support:ticket_detail', ticket_id=ticket_id)

@login_required
def close_ticket(request, ticket_id):
    """Close a support ticket"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        resolution_notes = request.POST.get('resolution_notes', '')
        
        with transaction.atomic():
            ticket.status = 'closed'
            ticket.resolved_at = timezone.now()
            ticket.closed_at = timezone.now()
            ticket.resolved_by = request.user.employee
            
            if resolution_notes:
                ticket.resolution_notes = resolution_notes
            
            ticket.save()
            
            # Add closure comment
            TicketComment.objects.create(
                ticket=ticket,
                author=request.user.employee,
                comment_type='status_update',
                comment=f"Ticket closed. Resolution: {resolution_notes}" if resolution_notes else "Ticket closed.",
                is_internal=False
            )
        
        messages.success(request, f'Ticket {ticket_id} has been closed successfully!')
    
    return redirect('support:ticket_detail', ticket_id=ticket_id)

@login_required
def ticket_stats_api(request):
    """API endpoint for ticket statistics (for AJAX/charts)"""
    # Monthly ticket trends
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    
    monthly_data = SupportTicket.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Category distribution
    category_data = SupportCategory.objects.annotate(
        ticket_count=Count('supportticket')
    ).values('name', 'ticket_count')
    
    # Response time averages
    avg_response_time = SupportTicket.objects.exclude(
        first_response_time__isnull=True
    ).aggregate(
        avg_hours=models.Avg(
            models.F('first_response_time') - models.F('created_at')
        )
    )
    
    return JsonResponse({
        'monthly_trends': list(monthly_data),
        'category_distribution': list(category_data),
        'avg_response_hours': avg_response_time['avg_hours'].total_seconds() / 3600 if avg_response_time['avg_hours'] else 0
    })

class OverdueTicketsView(LoginRequiredMixin, ListView):
    """View for overdue tickets"""
    template_name = 'support/overdue_tickets.html'
    context_object_name = 'tickets'
    paginate_by = 20
    
    def get_queryset(self):
        return SupportTicket.objects.filter(
            sla_due_date__lt=timezone.now(),
            status__in=['open', 'in_progress']
        ).select_related(
            'resident__user', 'property_ref', 'category', 'assigned_to'
        ).order_by('sla_due_date')

@login_required
def bulk_assign_tickets(request):
    """Bulk assign tickets to an employee"""
    if request.method == 'POST':
        ticket_ids = request.POST.getlist('ticket_ids')
        employee_id = request.POST.get('assigned_to')
        
        if ticket_ids and employee_id:
            employee = get_object_or_404(Employee, id=employee_id)
            
            tickets = SupportTicket.objects.filter(id__in=ticket_ids)
            updated_count = tickets.update(assigned_to=employee)
            
            # Create bulk assignment comment for each ticket
            for ticket in tickets:
                TicketComment.objects.create(
                    ticket=ticket,
                    author=request.user.employee,
                    comment_type='status_update',
                    comment=f"Ticket bulk assigned to {employee.user.get_full_name()}",
                    is_internal=True
                )
            
            messages.success(
                request, 
                f'{updated_count} tickets assigned to {employee.user.get_full_name()}'
            )
        else:
            messages.error(request, 'Please select tickets and an employee')
    
    return redirect('support:ticket_list')

@login_required 
def export_tickets(request):
    """Export tickets to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="support_tickets.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Ticket ID', 'Subject', 'Resident', 'Category', 'Priority', 
        'Status', 'Assigned To', 'Created Date', 'SLA Due Date', 'Resolved Date'
    ])
    
    tickets = SupportTicket.objects.select_related(
        'resident__user', 'category', 'assigned_to__user'
    ).all()
    
    for ticket in tickets:
        writer.writerow([
            ticket.ticket_id,
            ticket.subject,
            ticket.resident.user.get_full_name(),
            ticket.category.get_name_display(),
            ticket.get_priority_display(),
            ticket.get_status_display(),
            ticket.assigned_to.user.get_full_name() if ticket.assigned_to else '',
            ticket.created_at.strftime('%Y-%m-%d %H:%M'),
            ticket.sla_due_date.strftime('%Y-%m-%d %H:%M') if ticket.sla_due_date else '',
            ticket.resolved_at.strftime('%Y-%m-%d %H:%M') if ticket.resolved_at else ''
        ])
    
    return response



# Add these views to your existing support/views.py file

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from .models import SupportCategory
from .forms import SupportCategoryForm, CategoryFilterForm

class CategoryListView(LoginRequiredMixin, ListView):
    """List view for support categories with filtering"""
    model = SupportCategory
    template_name = 'support/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SupportCategory.objects.annotate(
            ticket_count=Count('supportticket'),
            open_ticket_count=Count('supportticket', filter=Q(supportticket__status='open'))
        ).order_by('priority_level', 'name')
        
        # Apply filters
        form = CategoryFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['priority_level']:
                queryset = queryset.filter(priority_level=form.cleaned_data['priority_level'])
            
            if form.cleaned_data['search']:
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(description__icontains=search_term)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = CategoryFilterForm(self.request.GET)
        context['total_categories'] = SupportCategory.objects.count()
        
        # Category statistics
        context['category_stats'] = {
            'high_priority': SupportCategory.objects.filter(priority_level=1).count(),
            'medium_priority': SupportCategory.objects.filter(priority_level=2).count(),
            'low_priority': SupportCategory.objects.filter(priority_level=3).count(),
            'total_tickets': SupportTicket.objects.count(),
        }
        
        return context

class CategoryDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a support category with ticket statistics"""
    model = SupportCategory
    template_name = 'support/category_detail.html'
    context_object_name = 'category'
    
    def get_object(self):
        return get_object_or_404(
            SupportCategory.objects.annotate(
                ticket_count=Count('supportticket'),
                open_tickets=Count('supportticket', filter=Q(supportticket__status='open')),
                in_progress_tickets=Count('supportticket', filter=Q(supportticket__status='in_progress')),
                resolved_tickets=Count('supportticket', filter=Q(supportticket__status='resolved'))
            ),
            pk=self.kwargs['pk']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Recent tickets in this category
        context['recent_tickets'] = self.object.supportticket_set.select_related(
            'resident__user', 'property_ref', 'assigned_to__user'
        ).order_by('-created_at')[:10]
        
        # Monthly ticket trends for this category
        from django.db.models.functions import TruncMonth
        context['monthly_trends'] = self.object.supportticket_set.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')[:6]  # Last 6 months
        
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create a new support category"""
    model = SupportCategory
    form_class = SupportCategoryForm
    template_name = 'support/category_create.html'
    success_url = reverse_lazy('support:category_list')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Support category "{form.instance.get_name_display()}" created successfully!'
        )
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing support category"""
    model = SupportCategory
    form_class = SupportCategoryForm
    template_name = 'support/category_update.html'
    context_object_name = 'category'

    def get_success_url(self):
        return reverse('support:category_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Support category "{form.instance}" updated successfully!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tickets = self.object.supportticket_set

        context.update({
            "total_tickets": tickets.count(),
            "open_tickets": tickets.filter(status="open").count(),
            "in_progress_tickets": tickets.filter(status="in_progress").count(),
            "resolved_tickets": tickets.filter(status="resolved").count(),
        })
        return context


@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    """Delete a support category (with safety checks)"""
    model = SupportCategory
    template_name = 'support/category_delete.html'
    success_url = reverse_lazy('support:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if category has associated tickets
        context['ticket_count'] = self.object.supportticket_set.count()
        context['open_ticket_count'] = self.object.supportticket_set.filter(status='open').count()
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Safety check - prevent deletion if there are tickets
        ticket_count = self.object.supportticket_set.count()
        if ticket_count > 0:
            messages.error(
                request,
                f'Cannot delete category "{self.object.get_name_display()}" because it has {ticket_count} associated tickets. '
                'Please reassign or resolve all tickets first.'
            )
            return redirect('support:category_detail', pk=self.object.pk)
        
        category_name = self.object.get_name_display()
        response = super().delete(request, *args, **kwargs)
        
        messages.success(
            request,
            f'Support category "{category_name}" deleted successfully!'
        )
        
        return response

@login_required
@require_http_methods(["POST"])
def bulk_update_category_sla(request):
    """Bulk update SLA hours for selected categories"""
    category_ids = request.POST.getlist('category_ids')
    new_sla_hours = request.POST.get('sla_hours')
    
    if category_ids and new_sla_hours:
        try:
            sla_hours = int(new_sla_hours)
            if 1 <= sla_hours <= 168:  # 1 hour to 1 week
                updated_count = SupportCategory.objects.filter(
                    id__in=category_ids
                ).update(sla_hours=sla_hours)
                
                messages.success(
                    request,
                    f'Updated SLA hours to {sla_hours} for {updated_count} categories'
                )
            else:
                messages.error(request, 'SLA hours must be between 1 and 168')
        except ValueError:
            messages.error(request, 'Invalid SLA hours value')
    else:
        messages.error(request, 'Please select categories and provide SLA hours')
    
    return redirect('support:category_list')

@login_required
def category_stats_api(request):
    """API endpoint for category statistics (for AJAX/charts)"""
    categories = SupportCategory.objects.annotate(
        total_tickets=Count('supportticket'),
        open_tickets=Count('supportticket', filter=Q(supportticket__status='open')),
        resolved_tickets=Count('supportticket', filter=Q(supportticket__status='resolved')),
        avg_resolution_time=models.Avg(
            models.F('supportticket__resolved_at') - models.F('supportticket__created_at'),
            filter=Q(supportticket__resolved_at__isnull=False)
        )
    ).values(
        'name', 'priority_level', 'sla_hours',
        'total_tickets', 'open_tickets', 'resolved_tickets', 'avg_resolution_time'
    )
    
    # Convert to list and format data
    category_data = []
    for category in categories:
        # Convert timedelta to hours for avg_resolution_time
        avg_hours = None
        if category['avg_resolution_time']:
            avg_hours = category['avg_resolution_time'].total_seconds() / 3600
        
        category_data.append({
            'name': category['name'],
            'display_name': dict(SupportCategory.CATEGORY_CHOICES)[category['name']],
            'priority_level': category['priority_level'],
            'sla_hours': category['sla_hours'],
            'total_tickets': category['total_tickets'],
            'open_tickets': category['open_tickets'],
            'resolved_tickets': category['resolved_tickets'],
            'avg_resolution_hours': round(avg_hours, 2) if avg_hours else None
        })
    
    return JsonResponse({
        'categories': category_data,
        'summary': {
            'total_categories': len(category_data),
            'total_tickets': sum(cat['total_tickets'] for cat in category_data),
            'total_open': sum(cat['open_tickets'] for cat in category_data),
        }
    })





