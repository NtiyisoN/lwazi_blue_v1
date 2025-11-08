from django.contrib import admin
from .models import (
    Skill, Industry, Location,
    InternProfile, EmployerProfile,
    InternDocument, Education, WorkExperience,
    InternshipPost, Conversation, Message
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['municipality', 'province', 'created_at']
    list_filter = ['province']
    search_fields = ['municipality', 'province']
    readonly_fields = ['created_at']


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'current_municipality', 'current_province', 'created_at']
    list_filter = ['current_province', 'created_at']
    search_fields = ['user__username', 'user__email', 'full_name', 'phone']
    filter_horizontal = ['skills', 'industries', 'preferred_locations']
    readonly_fields = ['created_at', 'updated_at', 'get_profile_completion_percentage']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('full_name', 'phone', 'date_of_birth', 'profile_photo', 'bio')
        }),
        ('Location', {
            'fields': ('current_location', 'current_municipality', 'current_province', 'preferred_locations')
        }),
        ('Preferences', {
            'fields': ('skills', 'industries')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at', 'get_profile_completion_percentage'),
            'classes': ('collapse',)
        }),
    )
    
    def get_profile_completion_percentage(self, obj):
        return f"{obj.get_profile_completion_percentage()}%"
    get_profile_completion_percentage.short_description = 'Profile Completion'


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'contact_person', 'municipality', 'province', 'created_at']
    list_filter = ['province', 'created_at']
    search_fields = ['company_name', 'user__username', 'user__email', 'contact_person']
    filter_horizontal = ['industries']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_logo', 'company_description', 'company_website')
        }),
        ('Contact', {
            'fields': ('contact_person', 'phone')
        }),
        ('Location', {
            'fields': ('company_location', 'municipality', 'province')
        }),
        ('Industries', {
            'fields': ('industries',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InternDocument)
class InternDocumentAdmin(admin.ModelAdmin):
    list_display = ['intern', 'document_type', 'version', 'is_latest', 'uploaded_at']
    list_filter = ['document_type', 'is_latest', 'uploaded_at']
    search_fields = ['intern__user__username', 'intern__full_name', 'description']
    readonly_fields = ['uploaded_at', 'version']
    
    fieldsets = (
        ('Document', {
            'fields': ('intern', 'document_type', 'document', 'description')
        }),
        ('Version Control', {
            'fields': ('version', 'is_latest', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['intern', 'qualification', 'institution', 'field_of_study', 'start_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['intern__user__username', 'institution', 'qualification', 'field_of_study']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Student', {
            'fields': ('intern',)
        }),
        ('Education Details', {
            'fields': ('institution', 'qualification', 'field_of_study', 'grade')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['intern', 'position', 'company', 'start_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['intern__user__username', 'company', 'position']
    filter_horizontal = ['skills_used']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Employee', {
            'fields': ('intern',)
        }),
        ('Position Details', {
            'fields': ('company', 'position', 'description')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Skills', {
            'fields': ('skills_used',)
        }),
    )


@admin.register(InternshipPost)
class InternshipPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'municipality', 'province', 'application_deadline', 
                    'is_published', 'is_active', 'views_count', 'created_at']
    list_filter = ['is_published', 'is_active', 'province', 'industry', 'created_at']
    search_fields = ['title', 'description', 'employer__company_name']
    filter_horizontal = ['skills_required']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'is_deadline_passed_status', 'days_until_deadline_display']
    date_hierarchy = 'application_deadline'
    
    fieldsets = (
        ('Employer', {
            'fields': ('employer',)
        }),
        ('Internship Details', {
            'fields': ('title', 'description', 'requirements', 'responsibilities')
        }),
        ('Requirements', {
            'fields': ('skills_required', 'industry')
        }),
        ('Location', {
            'fields': ('location', 'municipality', 'province')
        }),
        ('Duration & Compensation', {
            'fields': ('duration_months', 'stipend')
        }),
        ('Dates', {
            'fields': ('start_date', 'application_deadline', 'is_deadline_passed_status', 'days_until_deadline_display')
        }),
        ('Status', {
            'fields': ('is_active', 'is_published', 'views_count')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_deadline_passed_status(self, obj):
        """Show if deadline has passed"""
        return obj.is_deadline_passed()
    is_deadline_passed_status.boolean = True
    is_deadline_passed_status.short_description = 'Deadline Passed'
    
    def days_until_deadline_display(self, obj):
        """Show days until deadline"""
        days = obj.days_until_deadline
        if days == 0:
            return 'Expired'
        return f'{days} days'
    days_until_deadline_display.short_description = 'Days Until Deadline'
    
    actions = ['publish_internships', 'unpublish_internships', 'mark_inactive']
    
    def publish_internships(self, request, queryset):
        """Publish selected internships"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} internship(s) published.')
    publish_internships.short_description = 'Publish selected internships'
    
    def unpublish_internships(self, request, queryset):
        """Unpublish selected internships"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} internship(s) unpublished.')
    unpublish_internships.short_description = 'Unpublish selected internships'
    
    def mark_inactive(self, request, queryset):
        """Mark selected internships as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} internship(s) marked as inactive.')
    mark_inactive.short_description = 'Mark selected internships as inactive'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['employer_name', 'intern_name', 'last_message_at', 'created_at', 'message_count']
    list_filter = ['created_at', 'last_message_at']
    search_fields = ['intern__user__username', 'employer__company_name', 'intern__full_name']
    readonly_fields = ['created_at', 'updated_at', 'last_message_at']
    
    def employer_name(self, obj):
        return obj.employer.company_name
    employer_name.short_description = 'Employer'
    
    def intern_name(self, obj):
        return obj.intern.full_name or obj.intern.user.username
    intern_name.short_description = 'Intern'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender_user', 'conversation', 'message_preview', 'is_read', 'sent_at']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['sender_user__username', 'message']
    readonly_fields = ['sent_at', 'read_at']
    date_hierarchy = 'sent_at'
    
    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    message_preview.short_description = 'Message'
