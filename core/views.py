from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from .models import (
    InternProfile, EmployerProfile, InternDocument,
    Education, WorkExperience, Skill, Industry, Location
)
from .forms import (
    InternProfileForm, EmployerProfileForm, DocumentUploadForm,
    EducationForm, WorkExperienceForm
)


# =====================================================
# STATIC PAGES
# =====================================================

def home(request):
    """Landing page view with recent blog posts"""
    from blog.models import BlogPost
    
    recent_blogs = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:3]
    
    context = {
        'recent_blogs': recent_blogs,
    }
    
    return render(request, 'core/static/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'core/static/about.html')


def contact(request):
    """Contact page view"""
    return render(request, 'core/static/contact.html')


# Error handlers
def handler404(request, exception):
    """404 error handler"""
    return render(request, 'errors/404.html', status=404)


def handler403(request, exception):
    """403 error handler"""
    return render(request, 'errors/403.html', status=403)


def handler500(request):
    """500 error handler"""
    return render(request, 'errors/500.html', status=500)


def handler400(request, exception):
    """400 error handler"""
    return render(request, 'errors/400.html', status=400)


# =====================================================
# DASHBOARD
# =====================================================

@login_required
def dashboard(request):
    """Dashboard view - routes based on user type"""
    user = request.user
    
    if user.user_type == 'intern':
        # Get or create intern profile
        profile, created = InternProfile.objects.get_or_create(user=user)
        completion = profile.get_profile_completion_percentage()
        
        # Get statistics
        from applications.models import Application
        applications = Application.objects.filter(intern=profile)
        recent_applications = applications.order_by('-applied_at')[:5]
        
        # Get matched internships preview (top 5)
        from .services.matching import InternshipMatchingService
        matching_service = InternshipMatchingService()
        matched_internships = matching_service.get_matched_internships(profile, limit=5)
        
        # Get unread messages count
        unread_messages = Message.objects.filter(
            conversation__intern=profile,
            is_read=False
        ).exclude(sender_user=user).count()
        
        context = {
            'profile': profile,
            'completion_percentage': completion,
            'needs_profile_setup': completion < 50,
            'total_applications': applications.count(),
            'recent_applications': recent_applications,
            'matched_internships': matched_internships,
            'unread_messages': unread_messages,
        }
        return render(request, 'core/dashboard/intern_dashboard.html', context)
    
    elif user.user_type == 'employer':
        # Get or create employer profile
        try:
            profile = EmployerProfile.objects.get(user=user)
            needs_setup = False
        except EmployerProfile.DoesNotExist:
            profile = None
            needs_setup = True
        
        if not needs_setup:
            # Get statistics
            from applications.models import Application
            
            active_internships = InternshipPost.objects.filter(
                employer=profile,
                is_active=True,
                is_published=True
            )
            
            # Get all applications for employer's internships
            total_applications = Application.objects.filter(
                internship__employer=profile
            ).count()
            
            # Recent applications
            recent_applications = Application.objects.filter(
                internship__employer=profile
            ).select_related('intern', 'intern__user', 'internship').order_by('-applied_at')[:5]
            
            # Recent conversations with unread counts
            recent_conversations = Conversation.objects.filter(
                employer=profile
            ).select_related('intern', 'intern__user').order_by('-last_message_at')[:5]
            
            # Add unread count to each conversation
            for conversation in recent_conversations:
                conversation.unread_count = conversation.get_unread_count(user)
            
            # Unread messages
            unread_messages = Message.objects.filter(
                conversation__employer=profile,
                is_read=False
            ).exclude(sender_user=user).count()
            
            context = {
                'profile': profile,
                'needs_profile_setup': needs_setup,
                'active_internships_count': active_internships.count(),
                'active_internships': active_internships[:5],
                'total_applications': total_applications,
                'recent_applications': recent_applications,
                'recent_conversations': recent_conversations,
                'unread_messages': unread_messages,
            }
        else:
            context = {
                'profile': profile,
                'needs_profile_setup': needs_setup,
            }
        
        return render(request, 'core/dashboard/employer_dashboard.html', context)
    
    else:
        return render(request, 'core/dashboard/admin_dashboard.html')


# =====================================================
# PROFILE VIEWS
# =====================================================

@login_required
def profile(request):
    """Profile view - redirects to appropriate profile based on user type"""
    if request.user.user_type == 'intern':
        return intern_profile_view(request)
    elif request.user.user_type == 'employer':
        return employer_profile_view(request)
    else:
        return redirect('core:dashboard')


@login_required
def intern_profile_view(request):
    """View/edit intern profile"""
    profile, created = InternProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = InternProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = InternProfileForm(instance=profile)
    
    # Get related data
    documents = profile.documents.filter(is_latest=True)
    education = profile.education_set.all()
    work_experience = profile.work_experience_set.all()
    
    context = {
        'form': form,
        'profile': profile,
        'documents': documents,
        'education': education,
        'work_experience': work_experience,
        'completion_percentage': profile.get_profile_completion_percentage(),
    }
    
    return render(request, 'core/profiles/intern_profile.html', context)


@login_required
def employer_profile_view(request):
    """View/edit employer profile"""
    try:
        profile = EmployerProfile.objects.get(user=request.user)
        created = False
    except EmployerProfile.DoesNotExist:
        profile = None
        created = True
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Company profile updated successfully!')
            return redirect('core:profile')
    else:
        form = EmployerProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'is_new': created,
    }
    
    return render(request, 'core/profiles/employer_profile.html', context)


def intern_profile_public_view(request, username):
    """Public view of intern profile (for employers)"""
    from accounts.models import CustomUser
    
    intern_user = get_object_or_404(CustomUser, username=username, user_type='intern')
    profile = get_object_or_404(InternProfile, user=intern_user)
    
    # Get related data
    education = profile.education_set.all()
    work_experience = profile.work_experience_set.all()
    
    context = {
        'profile': profile,
        'intern_user': intern_user,
        'education': education,
        'work_experience': work_experience,
    }
    
    return render(request, 'core/profiles/intern_profile_public.html', context)


# =====================================================
# DOCUMENT MANAGEMENT
# =====================================================

@login_required
def document_upload_view(request):
    """Upload a document"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.intern = profile
            document.save()
            messages.success(request, f'{document.get_document_type_display()} uploaded successfully!')
            return redirect('core:profile')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'core/profiles/document_upload.html', {'form': form})


@login_required
def document_delete_view(request, document_id):
    """Soft delete a document (mark as not latest)"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    document = get_object_or_404(InternDocument, id=document_id, intern=profile)
    
    if request.method == 'POST':
        document.is_latest = False
        document.save()
        messages.success(request, 'Document removed successfully.')
    
    return redirect('core:profile')


# =====================================================
# EDUCATION MANAGEMENT
# =====================================================

@login_required
def education_create_view(request):
    """Add education record"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.intern = profile
            education.save()
            messages.success(request, 'Education record added successfully!')
            return redirect('core:profile')
    else:
        form = EducationForm()
    
    return render(request, 'core/profiles/education_form.html', {'form': form, 'action': 'Add'})


@login_required
def education_update_view(request, education_id):
    """Edit education record"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    education = get_object_or_404(Education, id=education_id, intern=profile)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education record updated successfully!')
            return redirect('core:profile')
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'core/profiles/education_form.html', {
        'form': form,
        'education': education,
        'action': 'Edit'
    })


@login_required
def education_delete_view(request, education_id):
    """Delete education record"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    education = get_object_or_404(Education, id=education_id, intern=profile)
    
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education record deleted successfully.')
    
    return redirect('core:profile')


# =====================================================
# WORK EXPERIENCE MANAGEMENT
# =====================================================

@login_required
def work_experience_create_view(request):
    """Add work experience"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.intern = profile
            experience.save()
            form.save_m2m()  # Save skills
            messages.success(request, 'Work experience added successfully!')
            return redirect('core:profile')
    else:
        form = WorkExperienceForm()
    
    return render(request, 'core/profiles/experience_form.html', {'form': form, 'action': 'Add'})


@login_required
def work_experience_update_view(request, experience_id):
    """Edit work experience"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    experience = get_object_or_404(WorkExperience, id=experience_id, intern=profile)
    
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work experience updated successfully!')
            return redirect('core:profile')
    else:
        form = WorkExperienceForm(instance=experience)
    
    return render(request, 'core/profiles/experience_form.html', {
        'form': form,
        'experience': experience,
        'action': 'Edit'
    })


@login_required
def work_experience_delete_view(request, experience_id):
    """Delete work experience"""
    if request.user.user_type != 'intern':
        return HttpResponseForbidden()
    
    profile = get_object_or_404(InternProfile, user=request.user)
    experience = get_object_or_404(WorkExperience, id=experience_id, intern=profile)
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Work experience deleted successfully.')
    
    return redirect('core:profile')


# =====================================================
# EXPLORE / BROWSE (MATCHING ALGORITHM)
# =====================================================

from .services.matching import InternshipMatchingService, InternMatchingService


@login_required
def explore(request):
    """
    Explore/browse view - Routes based on user type
    Uses matching algorithm when no filters applied
    """
    if request.user.user_type == 'intern':
        return intern_explore_view(request)
    elif request.user.user_type == 'employer':
        return employer_explore_view(request)
    else:
        return redirect('core:dashboard')


@login_required
def intern_explore_view(request):
    """
    Interns browse matched internships
    Uses matching algorithm when no filters applied
    """
    profile, created = InternProfile.objects.get_or_create(user=request.user)
    
    # Check if filters are applied
    has_filters = any(request.GET.values())
    
    if has_filters:
        # Use search/filter (same as internship_list_view)
        internships = InternshipPost.objects.filter(
            is_published=True,
            is_active=True
        ).select_related('employer', 'employer__user', 'industry')
        
        form = InternshipSearchForm(request.GET)
        
        if form.is_valid():
            # Text search
            query = form.cleaned_data.get('query')
            if query:
                internships = internships.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(employer__company_name__icontains=query)
                )
            
            # Filter by skills
            skills = form.cleaned_data.get('skills')
            if skills:
                for skill in skills:
                    internships = internships.filter(skills_required=skill)
            
            # Filter by industry
            industry = form.cleaned_data.get('industry')
            if industry:
                internships = internships.filter(industry=industry)
            
            # Filter by province
            province = form.cleaned_data.get('province')
            if province:
                internships = internships.filter(province=province)
            
            # Filter by minimum stipend
            stipend_min = form.cleaned_data.get('stipend_min')
            if stipend_min:
                internships = internships.filter(stipend__gte=stipend_min)
            
            # Filter by maximum duration
            duration_max = form.cleaned_data.get('duration_max')
            if duration_max:
                internships = internships.filter(duration_months__lte=duration_max)
        
        # Pagination
        paginator = Paginator(internships, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        matched_internships = [(internship, None) for internship in page_obj]
        show_match_scores = False
    else:
        # Use matching algorithm
        matching_service = InternshipMatchingService()
        matched_internships = matching_service.get_matched_internships(profile, limit=20)
        form = InternshipSearchForm()
        page_obj = None
        show_match_scores = True
    
    context = {
        'matched_internships': matched_internships,
        'show_match_scores': show_match_scores,
        'form': form,
        'internships': page_obj,
        'has_filters': has_filters,
        'profile': profile,
    }
    
    return render(request, 'core/matching/intern_explore.html', context)


@login_required
def employer_explore_view(request):
    """
    Employers browse matched interns
    Uses matching algorithm when no filters applied
    Shows profile photo thumbnails with advanced search
    """
    if request.user.user_type != 'employer':
        return HttpResponseForbidden()
    
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your company profile first.')
        return redirect('core:profile')
    
    # Check if filters are applied
    has_filters = any(request.GET.values())
    
    if has_filters:
        # Use advanced search with InternFilterForm
        from .forms import InternFilterForm
        from .services.search import SearchService
        
        form = InternFilterForm(request.GET)
        
        if form.is_valid():
            query = form.cleaned_data.get('query', '')
            filters = {
                'skills': [s.id for s in form.cleaned_data.get('skills', [])],
                'industries': [i.id for i in form.cleaned_data.get('industries', [])],
                'province': form.cleaned_data.get('province'),
                'has_experience': form.cleaned_data.get('has_experience'),
                'has_education': form.cleaned_data.get('has_education'),
            }
            
            interns = SearchService.search_interns(query, filters)
        else:
            interns = InternProfile.objects.filter(user__email_confirmed=True)
            form = InternFilterForm()
        
        # Pagination
        paginator = Paginator(interns, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        matched_interns = [(intern, None) for intern in page_obj]
        show_match_scores = False
    else:
        # Use matching algorithm
        matching_service = InternMatchingService()
        matched_interns = matching_service.get_matched_interns(employer_profile, limit=20)
        page_obj = None
        show_match_scores = True
        from .forms import InternFilterForm
        form = InternFilterForm()
    
    context = {
        'matched_interns': matched_interns,
        'show_match_scores': show_match_scores,
        'has_filters': has_filters,
        'internships': page_obj,
        'form': form,
    }
    
    return render(request, 'core/matching/employer_explore.html', context)


# =====================================================
# MESSAGING SYSTEM
# =====================================================

from .models import Conversation, Message
from .forms import MessageForm, StartConversationForm
from django.http import JsonResponse


@login_required
def messages_list(request):
    """
    List all conversations for the user
    Shows recent chats with unread count badges
    """
    if request.user.user_type == 'intern':
        try:
            intern_profile = InternProfile.objects.get(user=request.user)
            conversations = Conversation.objects.filter(
                intern=intern_profile
            ).select_related('employer', 'employer__user').prefetch_related('messages')
        except InternProfile.DoesNotExist:
            conversations = []
    elif request.user.user_type == 'employer':
        try:
            employer_profile = EmployerProfile.objects.get(user=request.user)
            conversations = Conversation.objects.filter(
                employer=employer_profile
            ).select_related('intern', 'intern__user').prefetch_related('messages')
        except EmployerProfile.DoesNotExist:
            conversations = []
    else:
        conversations = []
    
    # Add unread count to each conversation
    conversations_with_unread = []
    for conv in conversations:
        unread_count = conv.get_unread_count(request.user)
        conversations_with_unread.append((conv, unread_count))
    
    context = {
        'conversations': conversations_with_unread,
        'total_count': len(conversations),
    }
    
    return render(request, 'core/messages/conversation_list.html', context)


from django.views.decorators.cache import never_cache


@login_required
@never_cache
def conversation_detail_view(request, conversation_id):
    """
    View conversation messages and send new messages
    Marks messages as read when viewed
    """
    conversation = get_object_or_404(
        Conversation.objects.select_related('intern', 'intern__user', 'employer', 'employer__user'),
        pk=conversation_id
    )
    
    # Check permissions
    if request.user.user_type == 'intern':
        if conversation.intern.user != request.user:
            return HttpResponseForbidden()
    elif request.user.user_type == 'employer':
        if conversation.employer.user != request.user:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()
    
    # Get all messages ordered by sent time (oldest first for chronological display)
    chat_messages = conversation.messages.all().select_related('sender_user').order_by('sent_at')
    
    # Mark messages as read
    conversation.mark_messages_as_read(request.user)
    
    # Handle message sending
    if request.method == 'POST':
        print(f"📨 POST request received for conversation {conversation_id}")
        form = MessageForm(request.POST)
        print(f"📝 Form data: {request.POST}")
        
        if form.is_valid():
            print(f"✅ Form is valid")
            new_message = form.save(commit=False)
            new_message.conversation = conversation
            new_message.sender_user = request.user
            print(f"💾 Saving message from {request.user.username}...")
            new_message.save()
            print(f"✅ Message saved! ID: {new_message.pk}")
            
            # Update conversation's last_message_at manually (in case signal doesn't fire)
            conversation.last_message_at = new_message.sent_at
            conversation.save(update_fields=['last_message_at'])
            print(f"✅ Conversation updated")
            
            # Force redirect with GET to refresh the page and show new message
            messages.success(request, 'Message sent!')
            print(f"🔄 Redirecting to conversation detail...")
            
            # Use PRG (Post-Redirect-Get) pattern to avoid duplicate submissions
            return HttpResponseRedirect(reverse('core:conversation_detail', kwargs={'conversation_id': conversation.pk}))
        else:
            # Form validation failed
            print(f"❌ Form validation failed: {form.errors}")
            messages.error(request, f'Message could not be sent. {form.errors}')
    else:
        form = MessageForm()
    
    context = {
        'conversation': conversation,
        'chat_messages': chat_messages,  # Renamed to avoid conflict with Django messages
        'form': form,
        'is_employer': request.user.user_type == 'employer',
    }
    
    return render(request, 'core/messages/conversation_detail.html', context)


@login_required
def start_conversation_view(request, intern_username):
    """
    Employer starts a conversation with an intern
    Creates conversation if doesn't exist, sends first message
    """
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can initiate conversations.')
        return redirect('core:home')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    
    # Get intern by username
    from accounts.models import CustomUser
    intern_user = get_object_or_404(CustomUser, username=intern_username, user_type='intern')
    intern_profile = get_object_or_404(InternProfile, user=intern_user)
    
    if request.method == 'POST':
        form = StartConversationForm(request.POST)
        if form.is_valid():
            # Get or create conversation
            conversation, created = Conversation.objects.get_or_create(
                intern=intern_profile,
                employer=employer_profile
            )
            
            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender_user=request.user,
                message=form.cleaned_data['message']
            )
            
            messages.success(request, 'Message sent successfully!')
            return redirect('core:conversation_detail', conversation_id=conversation.pk)
    else:
        form = StartConversationForm()
    
    context = {
        'form': form,
        'intern': intern_profile,
    }
    
    return render(request, 'core/messages/start_conversation.html', context)


# =====================================================
# INTERNSHIP POSTING SYSTEM
# =====================================================

from .models import InternshipPost
from .forms import InternshipPostForm, InternshipSearchForm
from django.core.paginator import Paginator
from django.db.models import Q


def internship_list_view(request):
    """Browse/search internships - available to all (interns browse, employers can view)"""
    # Start with published and active internships
    internships = InternshipPost.objects.filter(
        is_published=True,
        is_active=True
    ).select_related('employer', 'employer__user', 'industry').prefetch_related('skills_required')
    
    # Search and filter
    form = InternshipSearchForm(request.GET or None)
    
    if form.is_valid():
        # Text search
        query = form.cleaned_data.get('query')
        if query:
            internships = internships.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(employer__company_name__icontains=query)
            )
        
        # Filter by skills
        skills = form.cleaned_data.get('skills')
        if skills:
            for skill in skills:
                internships = internships.filter(skills_required=skill)
        
        # Filter by industry
        industry = form.cleaned_data.get('industry')
        if industry:
            internships = internships.filter(industry=industry)
        
        # Filter by province
        province = form.cleaned_data.get('province')
        if province:
            internships = internships.filter(province=province)
        
        # Filter by minimum stipend
        stipend_min = form.cleaned_data.get('stipend_min')
        if stipend_min:
            internships = internships.filter(stipend__gte=stipend_min)
        
        # Filter by maximum duration
        duration_max = form.cleaned_data.get('duration_max')
        if duration_max:
            internships = internships.filter(duration_months__lte=duration_max)
    
    # Pagination
    paginator = Paginator(internships, 12)  # 12 internships per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'internships': page_obj,
        'total_count': internships.count(),
    }
    
    return render(request, 'core/internships/internship_list.html', context)


def internship_detail_view(request, pk):
    """Single internship detail view"""
    internship = get_object_or_404(
        InternshipPost.objects.select_related('employer', 'employer__user', 'industry'),
        pk=pk,
        is_published=True
    )
    
    # Increment view count
    internship.increment_views()
    
    # Check if user has applied
    has_applied = False
    if request.user.is_authenticated and request.user.user_type == 'intern':
        try:
            from applications.models import Application
            intern_profile = InternProfile.objects.get(user=request.user)
            has_applied = Application.objects.filter(
                internship=internship,
                intern=intern_profile
            ).first()
        except InternProfile.DoesNotExist:
            pass
    
    context = {
        'internship': internship,
        'has_applied': has_applied,
    }
    
    return render(request, 'core/internships/internship_detail.html', context)


@login_required
def internship_create_view(request):
    """Create new internship - employer only"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can post internships.')
        return redirect('core:dashboard')
    
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your company profile first.')
        return redirect('core:profile')
    
    if request.method == 'POST':
        form = InternshipPostForm(request.POST)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.employer = employer_profile
            internship.save()
            form.save_m2m()  # Save ManyToMany fields
            messages.success(request, 'Internship posted successfully!')
            return redirect('core:employer_internships')
    else:
        form = InternshipPostForm()
    
    return render(request, 'core/internships/internship_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def internship_update_view(request, pk):
    """Edit internship - employer only, own posts only"""
    if request.user.user_type != 'employer':
        return HttpResponseForbidden()
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    internship = get_object_or_404(InternshipPost, pk=pk, employer=employer_profile)
    
    if request.method == 'POST':
        form = InternshipPostForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            messages.success(request, 'Internship updated successfully!')
            return redirect('core:employer_internships')
    else:
        form = InternshipPostForm(instance=internship)
    
    return render(request, 'core/internships/internship_form.html', {
        'form': form,
        'internship': internship,
        'action': 'Edit'
    })


@login_required
def internship_delete_view(request, pk):
    """Soft delete internship - employer only, own posts only"""
    if request.user.user_type != 'employer':
        return HttpResponseForbidden()
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    internship = get_object_or_404(InternshipPost, pk=pk, employer=employer_profile)
    
    if request.method == 'POST':
        internship.is_active = False
        internship.save()
        messages.success(request, 'Internship deleted successfully.')
    
    return redirect('core:employer_internships')


@login_required
def employer_internships_view(request):
    """Employer's internship dashboard - view all posted internships"""
    if request.user.user_type != 'employer':
        return HttpResponseForbidden()
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    
    # Get all internships (active and inactive) with optimized queries
    internships = InternshipPost.objects.filter(
        employer=employer_profile
    ).select_related('industry').prefetch_related('skills_required', 'applications').order_by('-created_at')
    
    # Separate by status
    active_internships = internships.filter(is_active=True, is_published=True)
    draft_internships = internships.filter(is_published=False)
    closed_internships = internships.filter(is_active=False)
    
    context = {
        'active_internships': active_internships,
        'draft_internships': draft_internships,
        'closed_internships': closed_internships,
        'total_count': internships.count(),
    }
    
    return render(request, 'core/internships/employer_internships.html', context)
