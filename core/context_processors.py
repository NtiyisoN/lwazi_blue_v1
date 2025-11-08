"""
Context processors for Lwazi Blue
Makes data available to all templates
"""

from django.db.models import Count, Q
from .models import Conversation, Message


def unread_counts(request):
    """
    Add unread message and notification counts to all templates
    """
    context = {
        'unread_messages_count': 0,
        'unread_notifications_count': 0,
    }
    
    if request.user.is_authenticated:
        # Get unread messages count
        if request.user.user_type == 'intern':
            try:
                from .models import InternProfile
                intern_profile = InternProfile.objects.get(user=request.user)
                # Count unread messages in all conversations
                unread_messages = Message.objects.filter(
                    conversation__intern=intern_profile,
                    is_read=False
                ).exclude(sender_user=request.user).count()
                context['unread_messages_count'] = unread_messages
            except:
                pass
        
        elif request.user.user_type == 'employer':
            try:
                from .models import EmployerProfile
                employer_profile = EmployerProfile.objects.get(user=request.user)
                # Count unread messages in all conversations
                unread_messages = Message.objects.filter(
                    conversation__employer=employer_profile,
                    is_read=False
                ).exclude(sender_user=request.user).count()
                context['unread_messages_count'] = unread_messages
            except:
                pass
        
        # Get unread notifications count
        from notifications.models import Notification
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        context['unread_notifications_count'] = unread_notifications
    
    return context

