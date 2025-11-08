from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator


# =====================================================
# SUPPORTING MODELS
# =====================================================

class Skill(models.Model):
    """Skills that interns can have and internships can require"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Industry(models.Model):
    """Industries for matching interns with opportunities"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Location(models.Model):
    """Locations (municipalities and provinces) in South Africa"""
    municipality = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['province', 'municipality']
        unique_together = ['municipality', 'province']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return f"{self.municipality}, {self.province}"


# =====================================================
# PROFILE MODELS
# =====================================================

# South African provinces
PROVINCE_CHOICES = (
    ('', 'Select Province'),
    ('EC', 'Eastern Cape'),
    ('FS', 'Free State'),
    ('GP', 'Gauteng'),
    ('KZN', 'KwaZulu-Natal'),
    ('LP', 'Limpopo'),
    ('MP', 'Mpumalanga'),
    ('NC', 'Northern Cape'),
    ('NW', 'North West'),
    ('WC', 'Western Cape'),
)


class InternProfile(models.Model):
    """Profile for interns/graduates"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intern_profile'
    )
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    bio = models.TextField(blank=True, help_text='Tell us about yourself')
    
    # Location
    current_location = models.CharField(max_length=200, blank=True)
    current_municipality = models.CharField(max_length=100, blank=True)
    current_province = models.CharField(
        max_length=10,
        choices=PROVINCE_CHOICES,
        blank=True
    )
    
    # Preferences
    preferred_locations = models.ManyToManyField(
        Location,
        blank=True,
        related_name='interested_interns'
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='interns'
    )
    industries = models.ManyToManyField(
        Industry,
        blank=True,
        related_name='interested_interns'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Intern Profile'
        verbose_name_plural = 'Intern Profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['current_province']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            self.full_name,
            self.phone,
            self.date_of_birth,
            self.profile_photo,
            self.bio,
            self.current_location,
        ]
        
        # Count filled fields
        filled_count = sum(1 for field in fields_to_check if field)
        
        # Check ManyToMany fields
        if self.skills.exists():
            filled_count += 1
        if self.industries.exists():
            filled_count += 1
        if self.preferred_locations.exists():
            filled_count += 1
        
        # Check related models
        if hasattr(self, 'education_set') and self.education_set.exists():
            filled_count += 1
        
        total_fields = 10  # Total checkable fields
        return int((filled_count / total_fields) * 100)
    
    @property
    def has_profile_photo(self):
        """Check if profile has a photo"""
        return bool(self.profile_photo)


class EmployerProfile(models.Model):
    """Profile for employers/companies"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employer_profile'
    )
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    company_description = models.TextField(
        help_text='Describe your company and what you do'
    )
    company_website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    
    # Location
    company_location = models.CharField(max_length=200)
    municipality = models.CharField(max_length=100)
    province = models.CharField(
        max_length=10,
        choices=PROVINCE_CHOICES
    )
    
    # Industries
    industries = models.ManyToManyField(
        Industry,
        blank=True,
        related_name='employers'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Employer Profile'
        verbose_name_plural = 'Employer Profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['province']),
        ]
    
    def __str__(self):
        return f"{self.company_name}"
    
    @property
    def has_company_logo(self):
        """Check if company has a logo"""
        return bool(self.company_logo)


# =====================================================
# DOCUMENT MANAGEMENT
# =====================================================

class InternDocument(models.Model):
    """Documents uploaded by interns with version control"""
    DOCUMENT_TYPE_CHOICES = (
        ('cv', 'CV/Resume'),
        ('qualification', 'Qualification Certificate'),
        ('id', 'ID Document'),
        ('transcript', 'Academic Transcript'),
        ('other', 'Other'),
    )
    
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    version = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_latest = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Intern Document'
        verbose_name_plural = 'Intern Documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['intern', 'document_type', 'is_latest']),
        ]
    
    def __str__(self):
        return f"{self.intern.user.username} - {self.get_document_type_display()} (v{self.version})"
    
    def increment_version(self):
        """Increment version number for re-uploads"""
        # Mark all previous versions of this document type as not latest
        InternDocument.objects.filter(
            intern=self.intern,
            document_type=self.document_type,
            is_latest=True
        ).exclude(pk=self.pk).update(is_latest=False)
        
        # Get the highest version number for this document type
        max_version = InternDocument.objects.filter(
            intern=self.intern,
            document_type=self.document_type
        ).aggregate(models.Max('version'))['version__max'] or 0
        
        self.version = max_version + 1
        self.is_latest = True


@receiver(pre_save, sender=InternDocument)
def update_document_version(sender, instance, **kwargs):
    """Signal to handle document versioning"""
    if not instance.pk:  # New document
        instance.increment_version()


# =====================================================
# EDUCATION & EXPERIENCE
# =====================================================

class Education(models.Model):
    """Education history for interns"""
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='education_set'
    )
    institution = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g., Distinction, Pass, GPA 3.5'
    )
    description = models.TextField(
        blank=True,
        help_text='Additional details about your studies'
    )
    
    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Education Records'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.qualification} at {self.institution}"


class WorkExperience(models.Model):
    """Work experience history for interns"""
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='work_experience_set'
    )
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(
        help_text='Describe your responsibilities and achievements'
    )
    skills_used = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='work_experiences'
    )
    
    class Meta:
        verbose_name = 'Work Experience'
        verbose_name_plural = 'Work Experiences'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"


# =====================================================
# INTERNSHIP POSTING SYSTEM
# =====================================================

class InternshipPost(models.Model):
    """Internship opportunities posted by employers"""
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name='internship_posts'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text='Describe the internship opportunity'
    )
    requirements = models.TextField(
        help_text='What qualifications and skills are required?'
    )
    responsibilities = models.TextField(
        help_text='What will the intern be doing?'
    )
    skills_required = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='internship_posts'
    )
    industry = models.ForeignKey(
        Industry,
        on_delete=models.SET_NULL,
        null=True,
        related_name='internship_posts'
    )
    
    # Location
    location = models.CharField(
        max_length=200,
        help_text='Full address or area'
    )
    municipality = models.CharField(max_length=100)
    province = models.CharField(
        max_length=10,
        choices=PROVINCE_CHOICES
    )
    
    # Duration and compensation
    duration_months = models.IntegerField(
        help_text='Duration in months'
    )
    stipend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly stipend (optional)'
    )
    
    # Dates
    start_date = models.DateField(
        help_text='Expected start date'
    )
    application_deadline = models.DateField(
        help_text='Last date to apply'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Is this internship still accepting applications?'
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Is this internship visible to interns?'
    )
    views_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Internship Post'
        verbose_name_plural = 'Internship Posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_published']),
            models.Index(fields=['application_deadline']),
            models.Index(fields=['employer']),
            models.Index(fields=['industry']),
            models.Index(fields=['province']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['title']),  # For search queries
        ]
    
    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"
    
    def is_deadline_passed(self):
        """Check if application deadline has passed"""
        from django.utils import timezone
        return timezone.now().date() > self.application_deadline
    
    def increment_views(self):
        """Increment the view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    @property
    def is_accepting_applications(self):
        """Check if internship is accepting applications"""
        return self.is_active and self.is_published and not self.is_deadline_passed()
    
    @property
    def days_until_deadline(self):
        """Calculate days remaining until deadline"""
        from django.utils import timezone
        if self.is_deadline_passed():
            return 0
        delta = self.application_deadline - timezone.now().date()
        return delta.days


# =====================================================
# MESSAGING SYSTEM
# =====================================================

class Conversation(models.Model):
    """Conversation between an intern and employer"""
    intern = models.ForeignKey(
        InternProfile,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        unique_together = ['intern', 'employer']
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['intern']),
            models.Index(fields=['employer']),
            models.Index(fields=['-last_message_at']),
        ]
    
    def __str__(self):
        return f"{self.employer.company_name} ↔ {self.intern.user.username}"
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender_user=user).count()
    
    def mark_messages_as_read(self, user):
        """Mark all messages in conversation as read for a user"""
        self.messages.filter(is_read=False).exclude(sender_user=user).update(
            is_read=True,
            read_at=timezone.now()
        )


class Message(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message = models.TextField(help_text='Your message')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['conversation', 'is_read']),
            models.Index(fields=['sender_user']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        return f"{self.sender_user.username}: {self.message[:50]}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    """Send email notification when new message is sent"""
    if created:
        print(f"📬 Message signal triggered for message ID: {instance.pk}")
        
        # Check if email notifications are enabled
        from django.conf import settings
        if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True):
            print(f"📧 Email notifications disabled in settings")
            # Still update conversation timestamp
            instance.conversation.last_message_at = instance.sent_at
            instance.conversation.save(update_fields=['last_message_at'])
            return
        
        try:
            from core.email_service import send_email
            
            print(f"📧 Preparing email notification...")
            # Determine recipient
            if instance.sender_user.user_type == 'employer':
                recipient = instance.conversation.intern.user
                sender_name = instance.conversation.employer.company_name
            else:
                recipient = instance.conversation.employer.user
                sender_name = instance.conversation.intern.full_name or instance.conversation.intern.user.username
            
            subject = f'New Message from {sender_name}'
            message = f"""
Hello {recipient.username},<br>

You have received a new message from {sender_name}.

Message preview:<br>
\"{instance.message[:200]}{'...' if len(instance.message) > 200 else ''} \"<br>

Log in to your inbox to read and reply to this message.<br>

Best regards,<br>
The Lwazi Blue Team
            """
            
            print(f"📤 Attempting to send email to {recipient.email}...")
            # Send email using custom smtplib service (non-blocking - don't wait)
            try:
                send_email(recipient.email, subject, message, message)
                print(f"✅ Email sent successfully")
            except Exception as email_error:
                # Don't let email errors block message saving
                print(f"⚠️  Email notification failed (non-critical): {email_error}")
            
            # Update conversation last_message_at
            print(f"⏰ Updating conversation last_message_at...")
            instance.conversation.last_message_at = instance.sent_at
            instance.conversation.save(update_fields=['last_message_at'])
            print(f"✅ Signal completed successfully")
            
        except Exception as e:
            # Don't let signal errors block the request
            print(f"⚠️  Message notification signal error: {e}")
