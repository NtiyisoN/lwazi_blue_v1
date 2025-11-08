from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from core.models import InternshipPost, InternProfile, EmployerProfile
from .models import Application
from .forms import ApplicationForm, ApplicationStatusForm


@login_required
def application_create_view(request, internship_id):
    """
    Submit application for an internship
    Interns only, checks for duplicate applications
    """
    if request.user.user_type != 'intern':
        messages.error(request, 'Only interns can apply for internships.')
        return redirect('core:internship_list')
    
    # Get intern profile and internship
    intern_profile = get_object_or_404(InternProfile, user=request.user)
    internship = get_object_or_404(
        InternshipPost,
        pk=internship_id,
        is_published=True,
        is_active=True
    )
    
    # Check if already applied
    existing_application = Application.objects.filter(
        internship=internship,
        intern=intern_profile
    ).first()
    
    if existing_application:
        messages.warning(request, 'You have already applied for this internship.')
        return redirect('applications:detail', pk=existing_application.pk)
    
    # Check if deadline has passed
    if internship.is_deadline_passed():
        messages.error(request, 'The application deadline for this internship has passed.')
        return redirect('core:internship_detail', pk=internship_id)
    
    if request.method == 'POST':
        form = ApplicationForm(intern_profile, request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.intern = intern_profile
            application.save()
            form.save_m2m()  # Save additional documents
            
            messages.success(
                request,
                f'Application submitted successfully! You will be notified when the employer reviews your application.'
            )
            return redirect('applications:detail', pk=application.pk)
    else:
        form = ApplicationForm(intern_profile)
    
    context = {
        'form': form,
        'internship': internship,
        'intern_profile': intern_profile,
    }
    
    return render(request, 'applications/application_form.html', context)


@login_required
def application_detail_view(request, pk):
    """
    View application details
    Different views for intern vs employer
    """
    application = get_object_or_404(Application.objects.select_related(
        'intern', 'intern__user', 'internship', 'internship__employer'
    ), pk=pk)
    
    # Check permissions
    if request.user.user_type == 'intern':
        if application.intern.user != request.user:
            return HttpResponseForbidden()
    elif request.user.user_type == 'employer':
        if application.internship.employer.user != request.user:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()
    
    context = {
        'application': application,
        'is_employer': request.user.user_type == 'employer',
    }
    
    return render(request, 'applications/application_detail.html', context)


@login_required
def application_list_view(request):
    """
    Intern's applications dashboard
    Filter by status
    """
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    intern_profile = get_object_or_404(InternProfile, user=request.user)
    
    # Get all applications
    applications = Application.objects.filter(
        intern=intern_profile
    ).select_related('internship', 'internship__employer').order_by('-applied_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status counts for filtering
    status_counts = {}
    for status_code, status_name in Application.STATUS_CHOICES:
        count = Application.objects.filter(intern=intern_profile, status=status_code).count()
        status_counts[status_code] = count
    
    context = {
        'applications': page_obj,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'status_choices': Application.STATUS_CHOICES,
        'total_count': applications.count(),
    }
    
    return render(request, 'applications/application_list.html', context)


@login_required
def application_update_status_view(request, pk):
    """
    Employer updates application status
    Sends email notification to intern
    """
    if request.user.user_type != 'employer':
        return HttpResponseForbidden()
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    application = get_object_or_404(
        Application,
        pk=pk,
        internship__employer=employer_profile
    )
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Application status updated to {application.get_status_display()}. '
                f'Notification sent to {application.intern.user.email}.'
            )
            return redirect('applications:internship_applications', internship_id=application.internship.pk)
    else:
        form = ApplicationStatusForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
    }
    
    return render(request, 'applications/application_status_form.html', context)


@login_required
def internship_applications_view(request, internship_id):
    """
    Employer views applications for a specific internship
    Filter by status
    """
    if request.user.user_type != 'employer':
        return HttpResponseForbidden()
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    internship = get_object_or_404(
        InternshipPost,
        pk=internship_id,
        employer=employer_profile
    )
    
    # Get all applications for this internship
    applications = Application.objects.filter(
        internship=internship
    ).select_related('intern', 'intern__user').order_by('-applied_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status counts
    status_counts = {}
    for status_code, status_name in Application.STATUS_CHOICES:
        count = Application.objects.filter(internship=internship, status=status_code).count()
        status_counts[status_code] = count
    
    context = {
        'internship': internship,
        'applications': page_obj,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'total_count': applications.count(),
    }
    
    return render(request, 'applications/internship_applications.html', context)
