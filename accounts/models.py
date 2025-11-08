from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string
from datetime import timedelta


class CustomUser(AbstractUser):
    """
    Custom User Model with user type and email confirmation fields
    """
    USER_TYPE_CHOICES = (
        ('intern', 'Intern'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='intern',
        help_text='Type of user account'
    )
    email = models.EmailField(
        unique=True,
        help_text='Email address (must be unique)'
    )
    email_confirmed = models.BooleanField(
        default=False,
        help_text='Whether the email has been confirmed'
    )
    email_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the email was confirmed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Make email required for registration
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def confirm_email(self):
        """Mark email as confirmed"""
        self.email_confirmed = True
        self.email_confirmed_at = timezone.now()
        self.save(update_fields=['email_confirmed', 'email_confirmed_at'])
    
    @property
    def is_intern(self):
        return self.user_type == 'intern'
    
    @property
    def is_employer(self):
        return self.user_type == 'employer'
    
    @property
    def is_platform_admin(self):
        return self.user_type == 'admin'


class OTPToken(models.Model):
    """
    One-Time Password Token for email confirmation and login
    """
    OTP_TYPE_CHOICES = (
        ('email_confirmation', 'Email Confirmation'),
        ('login', 'Login'),
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='otp_tokens'
    )
    otp_code = models.CharField(
        max_length=6,
        help_text='6-digit OTP code'
    )
    otp_type = models.CharField(
        max_length=20,
        choices=OTP_TYPE_CHOICES,
        help_text='Purpose of this OTP'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text='When this OTP expires'
    )
    is_used = models.BooleanField(
        default=False,
        help_text='Whether this OTP has been used'
    )
    
    class Meta:
        verbose_name = 'OTP Token'
        verbose_name_plural = 'OTP Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['otp_code', 'otp_type']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_otp_type_display()} - {self.otp_code}"
    
    def save(self, *args, **kwargs):
        """Generate OTP code and expiry time on creation"""
        if not self.pk:  # Only on creation
            if not self.otp_code:
                self.otp_code = self.generate_otp()
            if not self.expires_at:
                self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def is_expired(self):
        """Check if OTP is expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    @classmethod
    def create_otp(cls, user, otp_type):
        """
        Create a new OTP for a user
        Invalidates any existing unused OTPs of the same type
        """
        # Invalidate existing unused OTPs of the same type
        cls.objects.filter(
            user=user,
            otp_type=otp_type,
            is_used=False
        ).update(is_used=True)
        
        # Create new OTP
        return cls.objects.create(user=user, otp_type=otp_type)
    
    @classmethod
    def verify_otp(cls, user, otp_code, otp_type):
        """
        Verify an OTP code for a user
        Returns the OTP token if valid, None otherwise
        """
        try:
            otp = cls.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type=otp_type,
                is_used=False
            )
            
            if otp.is_valid():
                return otp
            return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def cleanup_expired(cls):
        """Delete expired and used OTP tokens (for cleanup task)"""
        cutoff_date = timezone.now() - timedelta(days=7)
        cls.objects.filter(
            models.Q(expires_at__lt=timezone.now()) | models.Q(is_used=True),
            created_at__lt=cutoff_date
        ).delete()
