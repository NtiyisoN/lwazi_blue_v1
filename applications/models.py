from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import InternshipPost, InternProfile, InternDocument


class Application(models.Model):
    """
    Application submitted by intern for an internship
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('success', 'Accepted'),
        ('declined', 'Declined'),
        ('interview_pending', 'Interview Scheduled'),
        ('interview_success', 'Interview Passed'),
        ('interview_unsuccess', 'Interview Failed'),
        ('pending_final_decision', 'Pending Final Decision'),
    )
    
    internship = models.ForeignKey(
        InternshipPost,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )
    cover_letter = models.TextField(
        help_text='Explain why you are a good fit for this internship'
    )
    additional_documents = models.ManyToManyField(
        InternDocument,
        blank=True,
        related_name='applications',
        help_text='Select relevant documents to include with your application'
    )
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    
    # Employer feedback
    employer_notes = models.TextField(
        blank=True,
        help_text='Internal notes from employer (not visible to intern)'
    )
    
    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-applied_at']
        unique_together = ['internship', 'intern']
        indexes = [
            models.Index(fields=['status', 'applied_at']),
            models.Index(fields=['intern', 'status']),
        ]
    
    def __str__(self):
        return f"{self.intern.user.username} → {self.internship.title} ({self.get_status_display()})"
    
    def update_status(self, new_status, notes=''):
        """Update application status and send notification"""
        old_status = self.status
        self.status = new_status
        self.status_updated_at = timezone.now()
        if notes:
            self.employer_notes = notes
        self.save()
        
        # Signal will handle email notification
        return old_status
    
    @property
    def status_badge_class(self):
        """Return Bootstrap badge class for status"""
        status_classes = {
            'pending': 'bg-warning text-dark',
            'success': 'bg-success',
            'declined': 'bg-danger',
            'interview_pending': 'bg-info text-dark',
            'interview_success': 'bg-success',
            'interview_unsuccess': 'bg-danger',
            'pending_final_decision': 'bg-warning text-dark',
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    @property
    def can_update_status(self):
        """Check if status can still be updated"""
        final_statuses = ['success', 'declined', 'interview_unsuccess']
        return self.status not in final_statuses


@receiver(post_save, sender=Application)
def send_application_notification(sender, instance, created, **kwargs):
    """
    Send email notification when application is created or status changes
    """
    try:
        from core.email_service import send_email
        
        if created:
            # Send confirmation email to intern
            subject = f'Application Submitted - {instance.internship.title}'
            message = f"""
Hello {instance.intern.user.username},

Your application for "{instance.internship.title}" at {instance.internship.employer.company_name} has been successfully submitted.

Application Details:
- Position: {instance.internship.title}
- Company: {instance.internship.employer.company_name}
- Location: {instance.internship.municipality}, {instance.internship.province}
- Applied on: {instance.applied_at.strftime('%B %d, %Y at %I:%M %p')}

You will receive an email notification when the employer reviews your application.

You can track your application status in your dashboard.

Good luck!

Best regards,
The Lwazi Blue Team
            """
            
            # Send email using custom smtplib service (non-blocking)
            try:
                send_email(instance.intern.user.email, subject, message, message)
            except Exception as e:
                print(f"⚠️  Email notification failed (non-critical): {e}")
            
            # Notify employer
            employer_subject = f'New Application - {instance.internship.title}'
            employer_message = f"""
Hello {instance.internship.employer.user.username},

You have received a new application for "{instance.internship.title}".

Applicant: {instance.intern.full_name or instance.intern.user.username}
Applied on: {instance.applied_at.strftime('%B %d, %Y at %I:%M %p')}

Log in to your dashboard to review the application and update its status.

Best regards,
The Lwazi Blue Team
            """
            
            # Send email using custom smtplib service (non-blocking)
            try:
                send_email(instance.internship.employer.user.email, employer_subject, employer_message, employer_message)
            except Exception as e:
                print(f"⚠️  Email notification failed (non-critical): {e}")
        
        else:
            # Status changed - notify intern
            subject = f'Application Status Update - {instance.internship.title}'
            message = f"""
Hello {instance.intern.user.username},

Your application status for "{instance.internship.title}" at {instance.internship.employer.company_name} has been updated.

New Status: {instance.get_status_display()}
Updated on: {instance.status_updated_at.strftime('%B %d, %Y at %I:%M %p')}

Log in to your dashboard to view details.

Best regards,
The Lwazi Blue Team
            """
            
            # Send email using custom smtplib service (non-blocking)
            try:
                send_email(instance.intern.user.email, subject, message, message)
            except Exception as e:
                print(f"⚠️  Email notification failed (non-critical): {e}")
    
    except Exception as e:
        # Don't let signal errors block the request
        print(f"⚠️  Application notification signal error: {e}")
