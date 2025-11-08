from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm
from .services import NotificationService


@login_required
def notification_list(request):
    """List all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by read/unread
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Counts
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    total_count = Notification.objects.filter(user=request.user).count()
    
    context = {
        'notifications': page_obj,
        'filter_type': filter_type,
        'unread_count': unread_count,
        'total_count': total_count,
    }
    
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_read(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    # Return JSON if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        count = NotificationService.mark_all_as_read(request.user)
        messages.success(request, f'{count} notification(s) marked as read.')
    
    return redirect('notifications:list')


@login_required
def notification_settings(request):
    """Manage notification preferences"""
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully!')
            return redirect('notifications:settings')
    else:
        form = NotificationPreferenceForm(instance=prefs)
    
    return render(request, 'notifications/notification_settings.html', {'form': form})
