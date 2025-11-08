"""
Notification Service for Lwazi Blue
Handles creation and management of internal and email notifications
"""

from django.utils import timezone
from .models import Notification, NotificationPreference


class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def create_notification(user, notification_type, title, message, link=None):
        """
        Create an internal notification
        Check user preferences before creating
        """
        # Get or create user preferences
        prefs, created = NotificationPreference.objects.get_or_create(user=user)
        
        # Check if user wants internal notifications
        if prefs.internal_notifications:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                link=link
            )
            return notification
        return None
    
    @staticmethod
    def send_application_notification(application):
        """Create notification for application submission"""
        NotificationService.create_notification(
            user=application.intern.user,
            notification_type='application_submitted',
            title=f'Application Submitted',
            message=f'Your application for {application.internship.title} has been submitted successfully.',
            link=f'/applications/{application.pk}/'
        )
    
    @staticmethod
    def send_status_update_notification(application):
        """Create notification for application status update"""
        NotificationService.create_notification(
            user=application.intern.user,
            notification_type='application_status_update',
            title=f'Application Status Updated',
            message=f'Your application for {application.internship.title} status: {application.get_status_display()}',
            link=f'/applications/{application.pk}/'
        )
    
    @staticmethod
    def send_message_notification(message):
        """Create notification for new message"""
        # Determine recipient
        if message.sender_user.user_type == 'employer':
            recipient = message.conversation.intern.user
            sender_name = message.conversation.employer.company_name
        else:
            recipient = message.conversation.employer.user
            sender_name = message.conversation.intern.full_name or message.conversation.intern.user.username
        
        NotificationService.create_notification(
            user=recipient,
            notification_type='new_message',
            title=f'New message from {sender_name}',
            message=message.message[:100] + ('...' if len(message.message) > 100 else ''),
            link=f'/messages/{message.conversation.pk}/'
        )
    
    @staticmethod
    def send_matched_internship_notification(intern_user, internship):
        """Create notification for new matched internship"""
        NotificationService.create_notification(
            user=intern_user,
            notification_type='new_matched_internship',
            title=f'New Opportunity Matched',
            message=f'{internship.title} at {internship.employer.company_name} matches your profile!',
            link=f'/internships/{internship.pk}/'
        )
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a single notification as read"""
        try:
            notification = Notification.objects.get(pk=notification_id)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )

