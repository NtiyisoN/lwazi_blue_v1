from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['intern_name', 'internship_title', 'company_name', 
                    'status', 'applied_at', 'status_updated_at']
    list_filter = ['status', 'applied_at', 'internship__employer__company_name']
    search_fields = [
        'intern__user__username',
        'intern__full_name',
        'internship__title',
        'internship__employer__company_name'
    ]
    readonly_fields = ['applied_at', 'status_updated_at']
    filter_horizontal = ['additional_documents']
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Application', {
            'fields': ('internship', 'intern', 'status')
        }),
        ('Cover Letter', {
            'fields': ('cover_letter',)
        }),
        ('Documents', {
            'fields': ('additional_documents',)
        }),
        ('Employer Feedback', {
            'fields': ('employer_notes',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'status_updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def intern_name(self, obj):
        """Display intern name"""
        return obj.intern.full_name or obj.intern.user.username
    intern_name.short_description = 'Applicant'
    
    def internship_title(self, obj):
        """Display internship title"""
        return obj.internship.title
    internship_title.short_description = 'Internship'
    
    def company_name(self, obj):
        """Display company name"""
        return obj.internship.employer.company_name
    company_name.short_description = 'Company'
    
    actions = ['mark_as_success', 'mark_as_declined', 'mark_as_interview_pending']
    
    def mark_as_success(self, request, queryset):
        """Bulk accept applications"""
        updated = queryset.filter(status='pending').update(status='success')
        self.message_user(request, f'{updated} application(s) marked as accepted.')
    mark_as_success.short_description = 'Mark selected as Accepted'
    
    def mark_as_declined(self, request, queryset):
        """Bulk decline applications"""
        updated = queryset.filter(status='pending').update(status='declined')
        self.message_user(request, f'{updated} application(s) marked as declined.')
    mark_as_declined.short_description = 'Mark selected as Declined'
    
    def mark_as_interview_pending(self, request, queryset):
        """Bulk schedule interviews"""
        updated = queryset.filter(status='pending').update(status='interview_pending')
        self.message_user(request, f'{updated} application(s) marked for interview.')
    mark_as_interview_pending.short_description = 'Schedule Interview for selected'
