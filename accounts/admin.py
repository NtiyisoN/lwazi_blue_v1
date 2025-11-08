from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ['username', 'email', 'user_type', 'email_confirmed', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'email_confirmed', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'email_confirmed', 'email_confirmed_at')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'user_type')
        }),
    )
    
    actions = ['confirm_emails', 'make_intern', 'make_employer']
    
    def confirm_emails(self, request, queryset):
        """Bulk confirm emails"""
        updated = queryset.filter(email_confirmed=False).update(email_confirmed=True)
        self.message_user(request, f'{updated} user(s) email confirmed.')
    confirm_emails.short_description = 'Confirm selected users\' emails'
    
    def make_intern(self, request, queryset):
        """Change user type to intern"""
        updated = queryset.update(user_type='intern')
        self.message_user(request, f'{updated} user(s) changed to intern.')
    make_intern.short_description = 'Change selected users to Intern'
    
    def make_employer(self, request, queryset):
        """Change user type to employer"""
        updated = queryset.update(user_type='employer')
        self.message_user(request, f'{updated} user(s) changed to employer.')
    make_employer.short_description = 'Change selected users to Employer'


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    """OTP Token Admin"""
    list_display = ['user', 'otp_code', 'otp_type', 'is_used', 'created_at', 'expires_at', 'is_expired_status']
    list_filter = ['otp_type', 'is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'otp_code']
    readonly_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
    
    def is_expired_status(self, obj):
        """Show if OTP is expired"""
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Expired'
    
    actions = ['delete_expired']
    
    def delete_expired(self, request, queryset):
        """Delete expired and used OTP tokens"""
        count = queryset.filter(is_used=True).count() + queryset.filter(expires_at__lt=timezone.now()).count()
        OTPToken.cleanup_expired()
        self.message_user(request, f'{count} expired/used OTP token(s) deleted.')
    delete_expired.short_description = 'Delete expired/used OTP tokens'


from django.utils import timezone
