from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """Internal notifications for users"""
    NOTIFICATION_TYPE_CHOICES = (
        ('application_submitted', 'Application Submitted'),
        ('application_status_update', 'Application Status Update'),
        ('new_message', 'New Message'),
        ('new_matched_internship', 'New Matched Internship'),
        ('internship_deadline_reminder', 'Internship Deadline Reminder'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True, null=True, help_text='Link to related item')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def type_icon(self):
        """Return icon for notification type"""
        icons = {
            'application_submitted': 'bi-file-earmark-check',
            'application_status_update': 'bi-arrow-repeat',
            'new_message': 'bi-chat-dots',
            'new_matched_internship': 'bi-star',
            'internship_deadline_reminder': 'bi-clock-history',
        }
        return icons.get(self.notification_type, 'bi-bell')


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Email notification preferences
    email_application_submitted = models.BooleanField(
        default=True,
        help_text='Receive email when you submit an application'
    )
    email_application_status = models.BooleanField(
        default=True,
        help_text='Receive email when application status changes'
    )
    email_new_message = models.BooleanField(
        default=True,
        help_text='Receive email for new messages'
    )
    email_matched_internships = models.BooleanField(
        default=True,
        help_text='Receive email about new matched internships'
    )
    email_deadline_reminders = models.BooleanField(
        default=True,
        help_text='Receive email reminders about deadlines'
    )
    
    # Internal notification preference
    internal_notifications = models.BooleanField(
        default=True,
        help_text='Receive internal notifications in the platform'
    )
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"
