# Lwazi Blue - Detailed Implementation Plan

## Project Overview
A Django-based graduate placement platform connecting unemployed graduates with employers in South Africa. The platform features profile management, internship postings, intelligent matching algorithms, messaging, and comprehensive notification systems.

---

## Phase 1: Project Setup & Core Infrastructure

### 1.1 Django Project Initialization
- [ ] Create Django project `lwazi_blue`
- [ ] Set up virtual environment
- [ ] Install dependencies:
  - Django 4.2+
  - Pillow (image handling)
  - django-crispy-forms
  - Bootstrap 5
- [ ] Create `requirements.txt`
- [ ] Configure `settings.py`:
  - MEDIA_ROOT and MEDIA_URL
  - STATIC_ROOT and STATIC_URL
  - EMAIL_BACKEND (console for dev, SMTP for prod)
  - ALLOWED_HOSTS
  - Template directories
  - Static files configuration

### 1.2 Django Apps Structure
Create the following Django apps:
- [ ] `accounts` - User authentication and custom user model
- [ ] `core` - Main app with profiles, posts, messages
- [ ] `applications` - Application management
  - [ ] Will require `templatetags/` directory for custom filters
- [ ] `blog` - Blog functionality
- [ ] `notifications` - Notification system

**Note on Template Filters:**
Apps that use complex template logic (like dictionary access with variable keys) will need custom template filters. Create a `templatetags/` directory within the app with:
- `__init__.py` (empty file)
- `app_filters.py` (custom filter definitions)

Then load in templates with: `{% load app_filters %}`

### 1.3 Version Control & Documentation
- [ ] Initialize Git repository
- [ ] Create `.gitignore` (exclude media/, db.sqlite3, venv/, etc.)
- [ ] Create README.md with setup instructions
- [ ] Document environment variables needed

---

## Phase 2: User Authentication System (accounts app)

### 2.1 Custom User Model
**File:** `accounts/models.py`

Create CustomUser model extending AbstractUser:
- [ ] `user_type` field (choices: 'intern', 'employer', 'admin')
- [ ] `email` field (unique, required)
- [ ] `email_confirmed` boolean field (default: False)
- [ ] `email_confirmed_at` datetime field
- [ ] `created_at` timestamp
- [ ] `updated_at` timestamp
- [ ] Override USERNAME_FIELD = 'username'
- [ ] Set EMAIL_FIELD = 'email'

**File:** `accounts/models.py`

Create OTPToken model:
- [ ] `user` ForeignKey to CustomUser
- [ ] `otp_code` CharField (6 digits)
- [ ] `otp_type` CharField (choices: 'email_confirmation', 'login')
- [ ] `created_at` timestamp
- [ ] `expires_at` datetime
- [ ] `is_used` boolean field
- [ ] Method to generate random 6-digit OTP
- [ ] Method to check if OTP is expired (10 minutes validity)

### 2.2 Authentication Views
**File:** `accounts/views.py`

Implement views:
- [ ] `RegisterView` (GET/POST)
  - Form with username, email, password, user_type
  - Create user with email_confirmed=False
  - Send welcome email
  - Redirect to email confirmation page
  - Include link to email confirmation page
  
- [ ] `LoginView` (GET/POST)
  - Standard login form
  - Button to request OTP login
  - Check if email is confirmed before login
  - Redirect to dashboard on success
  
- [ ] `OTPLoginView` (GET/POST)
  - Form to request OTP via email
  - Form to submit OTP for login
  - Generate OTP token with type='login'
  - Send OTP via email
  - Validate OTP and log user in
  
- [ ] `EmailConfirmationView` (GET/POST)
  - Check URL params for email and otp
  - If both present, auto-trigger confirmation
  - If only email present, check if already confirmed
  - If already confirmed, show message with dashboard link
  - If not confirmed, show OTP input form
  - Button to request OTP
  - Button to confirm with OTP
  - Generate OTP token with type='email_confirmation'
  - Send confirmation email with OTP and clickable link
  - Mark email_confirmed=True on success
  
- [ ] `RequestOTPView` (POST, AJAX)
  - Generate new OTP
  - Send email with OTP
  - Return JSON response
  
- [ ] `LogoutView` (GET)
  - Log user out
  - Redirect to home page

### 2.3 Authentication Forms
**File:** `accounts/forms.py`

- [ ] `RegisterForm` - Username, email, password, user_type
- [ ] `LoginForm` - Username/email, password
- [ ] `OTPRequestForm` - Email field
- [ ] `OTPLoginForm` - Email, OTP code
- [ ] `EmailConfirmationForm` - OTP code

### 2.4 Authentication URLs
**File:** `accounts/urls.py`

- [ ] `/register/` - RegisterView
- [ ] `/login/` - LoginView
- [ ] `/logout/` - LogoutView
- [ ] `/email-confirmation/` - EmailConfirmationView
- [ ] `/request-otp/` - RequestOTPView (AJAX)
- [ ] `/otp-login/` - OTPLoginView

### 2.5 Authentication Templates
**Directory:** `templates/accounts/`

- [ ] `register.html` - Registration form
- [ ] `login.html` - Login form with OTP option
- [ ] `otp_login.html` - OTP login form
- [ ] `email_confirmation.html` - Email confirmation with OTP
- [ ] Email templates:
  - [ ] `emails/welcome.html`
  - [ ] `emails/otp_confirmation.html`
  - [ ] `emails/otp_login.html`

---

## Phase 3: Profile Management (core app)

### 3.1 Profile Models
**File:** `core/models.py`

**Important:** Add South African province choices before the models:
```python
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
```

Create InternProfile model:
- [ ] `user` OneToOneField to CustomUser
- [ ] `full_name` CharField
- [ ] `phone` CharField
- [ ] `date_of_birth` DateField
- [ ] `profile_photo` ImageField (upload_to='profile_photos/')
- [ ] `bio` TextField
- [ ] `current_location` CharField
- [ ] `current_municipality` CharField
- [ ] `current_province` CharField with PROVINCE_CHOICES
- [ ] `preferred_locations` ManyToManyField to Location model
- [ ] `skills` ManyToManyField to Skill model
- [ ] `industries` ManyToManyField to Industry model
- [ ] `created_at` timestamp
- [ ] `updated_at` timestamp
- [ ] Method to get profile completion percentage

**Note:** Use `choices=PROVINCE_CHOICES` for all province fields in:
- InternProfile.current_province
- EmployerProfile.province
- InternshipPost.province

Create EmployerProfile model:
- [ ] `user` OneToOneField to CustomUser
- [ ] `company_name` CharField
- [ ] `company_logo` ImageField
- [ ] `company_description` TextField
- [ ] `company_website` URLField
- [ ] `contact_person` CharField
- [ ] `phone` CharField
- [ ] `company_location` CharField
- [ ] `municipality` CharField
- [ ] `province` CharField
- [ ] `industries` ManyToManyField to Industry model
- [ ] `created_at` timestamp
- [ ] `updated_at` timestamp

Create supporting models:
- [ ] `Skill` model (name, slug, created_at)
- [ ] `Industry` model (name, slug, created_at)
- [ ] `Location` model (municipality, province, created_at)

### 3.2 Document Management Models
**File:** `core/models.py`

Create InternDocument model:
- [ ] `intern` ForeignKey to InternProfile
- [ ] `document_type` CharField (choices: 'cv', 'qualification', 'id', 'transcript', 'other')
- [ ] `document` FileField (upload_to='documents/')
- [ ] `version` IntegerField (default=1)
- [ ] `description` TextField
- [ ] `uploaded_at` timestamp
- [ ] `is_latest` BooleanField (default=True)
- [ ] Method to increment version on re-upload
- [ ] Signal to update is_latest flag

### 3.3 Education & Experience Models
**File:** `core/models.py`

Create Education model:
- [ ] `intern` ForeignKey to InternProfile
- [ ] `institution` CharField
- [ ] `qualification` CharField
- [ ] `field_of_study` CharField
- [ ] `start_date` DateField
- [ ] `end_date` DateField (nullable)
- [ ] `is_current` BooleanField
- [ ] `grade` CharField
- [ ] `description` TextField

Create WorkExperience model:
- [ ] `intern` ForeignKey to InternProfile
- [ ] `company` CharField
- [ ] `position` CharField
- [ ] `start_date` DateField
- [ ] `end_date` DateField (nullable)
- [ ] `is_current` BooleanField
- [ ] `description` TextField
- [ ] `skills_used` ManyToManyField to Skill

### 3.4 Profile Views
**File:** `core/views.py`

Implement views:
- [ ] `InternProfileView` (GET/POST) - View/edit intern profile
- [ ] `EmployerProfileView` (GET/POST) - View/edit employer profile
- [ ] `InternProfilePublicView` (GET) - Public view for employers
- [ ] `DocumentUploadView` (POST) - Upload/replace documents
- [ ] `DocumentDeleteView` (POST) - Soft delete documents
- [ ] `EducationCreateView` (POST) - Add education
- [ ] `EducationUpdateView` (POST) - Edit education
- [ ] `EducationDeleteView` (POST) - Delete education
- [ ] `WorkExperienceCreateView` (POST) - Add work experience
- [ ] `WorkExperienceUpdateView` (POST) - Edit work experience
- [ ] `WorkExperienceDeleteView` (POST) - Delete work experience

### 3.5 Profile Forms
**File:** `core/forms.py`

- [ ] `InternProfileForm` - All profile fields
- [ ] `EmployerProfileForm` - Company information
- [ ] `DocumentUploadForm` - Document type and file
- [ ] `EducationForm` - Education details
- [ ] `WorkExperienceForm` - Experience details

### 3.6 Profile Templates
**Directory:** `templates/core/profiles/`

- [ ] `intern_profile.html` - Intern profile edit with tabbed interface
  - [ ] Use Bootstrap tabs to organize sections (Basic Info, Documents, Education, Experience)
  - [ ] Sidebar with quick navigation links that sync with tabs
  - [ ] JavaScript to convert multi-select fields to toggle badges
  - [ ] See detailed implementation below
  
- [ ] `intern_profile_public.html` - Public intern profile view
- [ ] `employer_profile.html` - Employer profile edit
- [ ] Partials:
  - [ ] `_document_list.html`
  - [ ] `_education_list.html`
  - [ ] `_experience_list.html`

**Tabbed Profile Interface Implementation:**

The intern profile should use Bootstrap tabs for better UX:

1. **Tab Navigation:**
   - Create tabs for: Basic Information, Documents, Education, Work Experience
   - Use `data-bs-toggle="tab"` for tab functionality
   - Sync sidebar links with tab navigation using JavaScript

2. **Multi-Select Toggle Enhancement:**
   - Convert `preferred_locations`, `skills`, and `industries` from standard multi-select to clickable badges
   - Selected badges: `badge bg-primary`
   - Unselected badges: `badge bg-secondary`
   - JavaScript function `convertMultiSelectToToggles()` to transform fields
   - Hidden original select element maintains form submission

3. **JavaScript Requirements:**
```javascript
// Tab sync with sidebar
document.addEventListener('shown.bs.tab', function(event) {
    // Update sidebar active state when tabs change
});

// Convert multi-select to toggles
function convertMultiSelectToToggles(selectId, label) {
    // Hide original select
    // Create badge container
    // Generate clickable badges for each option
    // Toggle selection on click
}
```

---

## Phase 4: Internship Posting System (core app)

### 4.1 Internship Models
**File:** `core/models.py`

Create InternshipPost model:
- [ ] `employer` ForeignKey to EmployerProfile
- [ ] `title` CharField
- [ ] `description` TextField
- [ ] `requirements` TextField
- [ ] `responsibilities` TextField
- [ ] `skills_required` ManyToManyField to Skill
- [ ] `industry` ForeignKey to Industry
- [ ] `location` CharField
- [ ] `municipality` CharField
- [ ] `province` CharField
- [ ] `duration_months` IntegerField
- [ ] `stipend` DecimalField (nullable)
- [ ] `start_date` DateField
- [ ] `application_deadline` DateField
- [ ] `is_active` BooleanField (default=True)
- [ ] `is_published` BooleanField (default=False)
- [ ] `views_count` IntegerField (default=0)
- [ ] `created_at` timestamp
- [ ] `updated_at` timestamp
- [ ] Method to check if deadline passed
- [ ] Method to increment views

### 4.2 Internship Views
**File:** `core/views.py`

Implement views:
- [ ] `InternshipListView` (GET) - List all active internships
  - Pagination
  - Search and filter functionality
  - If no filters, use matching algorithm
  
- [ ] `InternshipDetailView` (GET) - Single internship details
  - Increment view count
  - Show application status if user applied
  
- [ ] `InternshipCreateView` (GET/POST) - Create internship (employer only)
- [ ] `InternshipUpdateView` (GET/POST) - Edit internship (employer only)
- [ ] `InternshipDeleteView` (POST) - Soft delete (set is_active=False)
- [ ] `EmployerInternshipListView` (GET) - Employer's internships dashboard

### 4.3 Internship Forms
**File:** `core/forms.py`

- [ ] `InternshipPostForm` - All internship fields
- [ ] `InternshipSearchForm` - Search and filter fields

### 4.4 Internship Templates
**Directory:** `templates/core/internships/`

- [ ] `internship_list.html` - Browse internships
- [ ] `internship_detail.html` - Single internship view
- [ ] `internship_form.html` - Create/edit internship
- [ ] `employer_internships.html` - Employer's internship dashboard
- [ ] Partials:
  - [ ] `_internship_card.html`
  - [ ] `_internship_filters.html`

---

## Phase 5: Matching Algorithm (core app)

### 5.1 Matching Service
**File:** `core/services/matching.py`

Create InternshipMatchingService class:
- [ ] Method: `get_matched_internships(intern_profile, limit=20)`
  - Calculate match scores based on:
    - Skills match (weight: 40%)
    - Industry match (weight: 25%)
    - Location match (weight: 20%)
    - Qualification level (weight: 15%)
  - Return queryset ordered by score
  
- [ ] Method: `calculate_match_score(internship, intern_profile)`
  - Returns score from 0-100
  
- [ ] Configurable weights in settings

Create InternMatchingService class:
- [ ] Method: `get_matched_interns(employer_profile, limit=20)`
  - Calculate match scores based on:
    - Skills match (weight: 40%)
    - Industry match (weight: 25%)
    - Location match (weight: 20%)
    - Experience level (weight: 15%)
  - Return queryset ordered by score
  
- [ ] Method: `calculate_match_score(intern_profile, employer_profile)`
  - Returns score from 0-100

### 5.2 Matching Views
**File:** `core/views.py`

- [ ] `InternExploreView` (GET) - Interns browse matched internships
  - Use matching algorithm when no filters applied
  - Support search/filter override
  
- [ ] `EmployerExploreView` (GET) - Employers browse matched interns
  - Use matching algorithm when no filters applied
  - Support search/filter override
  - Show profile photo thumbnails

### 5.3 Matching Templates
**Directory:** `templates/core/matching/`

- [ ] `intern_explore.html` - Matched internships for intern
- [ ] `employer_explore.html` - Matched interns for employer
- [ ] Partials:
  - [ ] `_intern_card.html` (with photo thumbnail)
  - [ ] `_match_score_badge.html`

---

## Phase 6: Application System (applications app)

### 6.1 Application Models
**File:** `applications/models.py`

Create Application model:
- [ ] `internship` ForeignKey to InternshipPost
- [ ] `intern` ForeignKey to InternProfile
- [ ] `status` CharField with choices:
  - 'pending'
  - 'success'
  - 'declined'
  - 'interview_pending'
  - 'interview_success'
  - 'interview_unsuccess'
  - 'pending_final_decision'
- [ ] `cover_letter` TextField
- [ ] `additional_documents` ManyToManyField to InternDocument
- [ ] `applied_at` timestamp
- [ ] `status_updated_at` timestamp
- [ ] `employer_notes` TextField
- [ ] Unique together constraint: (internship, intern)
- [ ] Signal to send email on status change

### 6.2 Application Views
**File:** `applications/views.py`

Implement views:
- [ ] `ApplicationCreateView` (POST) - Submit application
  - Check if already applied
  - Send confirmation email
  
- [ ] `ApplicationDetailView` (GET) - View application details
  - Different views for intern vs employer
  
- [ ] `ApplicationUpdateStatusView` (POST) - Employer updates status
  - Send email notification on status change
  
- [ ] `ApplicationListView` (GET) - Intern's applications dashboard
  - Filter by status
  - Show all applications with current status
  
- [ ] `InternshipApplicationsView` (GET) - Employer views applications for internship
  - Filter by status
  - Pagination

### 6.3 Application Forms
**File:** `applications/forms.py`

- [ ] `ApplicationForm` - Cover letter, documents
- [ ] `ApplicationStatusForm` - Status, employer notes

### 6.4 Application Templates
**Directory:** `templates/applications/`

- [ ] `application_form.html` - Submit application
- [ ] `application_detail.html` - Application details
  - [ ] **Important:** Display employer notes persistently using a card, not an alert
    ```django
    {% if is_employer and application.employer_notes %}
    <h5 class="mb-3"><i class="bi bi-sticky"></i> Internal Notes</h5>
    <div class="card bg-light border-secondary">
        <div class="card-body">
            <p class="mb-0" style="white-space: pre-line;">{{ application.employer_notes }}</p>
        </div>
    </div>
    {% endif %}
    ```
- [ ] `application_list.html` - Intern's applications
  - [ ] Load custom filters: `{% load app_filters %}`
  - [ ] Use `status_choices` for iteration
  - [ ] Use `get_item` filter for dictionary access
- [ ] `internship_applications.html` - Employer's view of applications
- [ ] Partials:
  - [ ] `_application_card.html`
  - [ ] `_status_badge.html`
  - [ ] `_status_update_form.html`

### 6.5 Custom Template Filters
**Directory:** `applications/templatetags/`

Django templates don't support dictionary access with variable keys by default.
Create custom filters for template operations:

- [ ] Create `applications/templatetags/` directory
- [ ] Create `applications/templatetags/__init__.py` (empty file)
- [ ] Create `applications/templatetags/app_filters.py`:

```python
from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a variable key.
    Usage: {{ my_dict|get_item:my_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
```

**Usage in templates:**
```django
{% load app_filters %}
{{ status_counts|get_item:status_code|default:0 }}
```

**Important:** Always pass `status_choices` in context alongside `status_counts`:
```python
context = {
    'status_counts': status_counts,  # Dictionary of counts
    'status_choices': Application.STATUS_CHOICES,  # List of tuples
}
```

---

## Phase 7: Messaging System (core app)

### 7.1 Message Models
**File:** `core/models.py`

Create Conversation model:
- [ ] `intern` ForeignKey to InternProfile
- [ ] `employer` ForeignKey to EmployerProfile
- [ ] `created_at` timestamp
- [ ] `updated_at` timestamp
- [ ] `last_message_at` timestamp
- [ ] Unique together: (intern, employer)
- [ ] Method to get unread count per user

Create Message model:
- [ ] `conversation` ForeignKey to Conversation
- [ ] `sender_user` ForeignKey to CustomUser
- [ ] `message` TextField
- [ ] `is_read` BooleanField (default=False)
- [ ] `read_at` timestamp
- [ ] `sent_at` timestamp
- [ ] Signal to send email notification

### 7.2 Message Views
**File:** `core/views.py`

Implement views:
- [ ] `ConversationListView` (GET) - List all conversations
  - Show recent chats
  - Unread count badges
  
- [ ] `ConversationDetailView` (GET) - View conversation messages
  - Mark messages as read
  - Load messages with AJAX for real-time feel
  
- [ ] `MessageSendView` (POST) - Send message
  - Employers can initiate
  - Interns can only reply
  - Send email notification
  
- [ ] `StartConversationView` (POST) - Employer starts conversation from intern detail
  - Modal form on intern detail page
  - Create conversation if doesn't exist
  - Send first message
  - Email notification to intern

### 7.3 Message Forms
**File:** `core/forms.py`

- [ ] `MessageForm` - Message text field
- [ ] `StartConversationForm` - Initial message field

### 7.4 Message Templates
**Directory:** `templates/core/messages/`

- [ ] `conversation_list.html` - Inbox/conversations list
- [ ] `conversation_detail.html` - Chat interface
- [ ] `_message_bubble.html` - Individual message partial
- [ ] `_start_conversation_modal.html` - Modal for starting chat
- [ ] Email template: `emails/new_message.html`

---

## Phase 8: Dashboard & Navigation (core app)

### 8.1 Dashboard Views
**File:** `core/views.py`

Create DashboardView:
- [ ] Route based on user type
- [ ] Intern dashboard shows:
  - Profile completion percentage
  - Recent applications with status
  - Matched internships preview
  - Unread messages count
  - Recent notifications
  
- [ ] Employer dashboard shows:
  - Active internships count
  - Total applications received
  - Recent applications
  - Recent chats with interns
  - Active internships list

**Important Template Consideration:**
- [ ] When displaying conversations with unread counts, calculate the count in the view
- [ ] Django templates cannot pass arguments to methods: `{% if obj.method(arg) %}` is invalid
- [ ] Solution: Pre-calculate in view and attach to object
  ```python
  for conversation in conversations:
      conversation.unread_count = conversation.get_unread_count(user)
  ```
- [ ] Then use in template: `{% if conversation.unread_count > 0 %}`

### 8.2 Navigation System
**File:** `templates/includes/navbar.html`

Implement conditional navigation:
- [ ] Guest users see: Home, About, Contact, Blog, Login, Register
- [ ] Logged-in users see:
  - Nav: Dashboard, Blog, Profile, Explore, Notifications, Settings, Logout
  - Footer: Home, About, Contact
- [ ] User type-specific navigation items
- [ ] Notification badge count
- [ ] Unread messages badge count

### 8.3 Dashboard Templates
**Directory:** `templates/core/dashboard/`

- [ ] `intern_dashboard.html` - Intern dashboard
- [ ] `employer_dashboard.html` - Employer dashboard
- [ ] Partials:
  - [ ] `_recent_applications.html`
  - [ ] `_matched_internships_preview.html`
  - [ ] `_stats_cards.html`

---

## Phase 9: Notification System (notifications app)

### 9.1 Notification Models
**File:** `notifications/models.py`

Create Notification model:
- [ ] `user` ForeignKey to CustomUser
- [ ] `notification_type` CharField with choices:
  - 'application_submitted'
  - 'application_status_update'
  - 'new_message'
  - 'new_matched_internship'
  - 'internship_deadline_reminder'
- [ ] `title` CharField
- [ ] `message` TextField
- [ ] `link` URLField (nullable)
- [ ] `is_read` BooleanField (default=False)
- [ ] `created_at` timestamp
- [ ] `read_at` timestamp

Create NotificationPreference model:
- [ ] `user` OneToOneField to CustomUser
- [ ] `email_application_submitted` BooleanField (default=True)
- [ ] `email_application_status` BooleanField (default=True)
- [ ] `email_new_message` BooleanField (default=True)
- [ ] `email_matched_internships` BooleanField (default=True)
- [ ] `email_deadline_reminders` BooleanField (default=True)
- [ ] `internal_notifications` BooleanField (default=True)

### 9.2 Notification Service
**File:** `notifications/services.py`

Create NotificationService class:
- [ ] Method: `create_notification(user, type, title, message, link=None)`
  - Create internal notification
  - Check preferences
  - Send email if enabled
  
- [ ] Method: `send_application_notification(application)`
- [ ] Method: `send_status_update_notification(application)`
- [ ] Method: `send_message_notification(message)`
- [ ] Method: `send_matched_internship_notification(intern, internship)`
- [ ] Method: `mark_as_read(notification_id)`
- [ ] Method: `mark_all_as_read(user)`

### 9.3 Notification Views
**File:** `notifications/views.py`

- [ ] `NotificationListView` (GET) - List all notifications
- [ ] `NotificationMarkReadView` (POST) - Mark notification as read
- [ ] `NotificationMarkAllReadView` (POST) - Mark all as read
- [ ] `NotificationSettingsView` (GET/POST) - Manage preferences

### 9.4 Notification Templates
**Directory:** `templates/notifications/`

- [ ] `notification_list.html` - Notifications page
- [ ] `notification_settings.html` - Preferences page
- [ ] `_notification_item.html` - Single notification partial
- [ ] Email templates for each notification type

---

## Phase 10: Blog System (blog app)

### 10.1 Blog Models
**File:** `blog/models.py`

Create BlogPost model:
- [ ] `author` ForeignKey to CustomUser (admin/internal only)
- [ ] `title` CharField
- [ ] `slug` SlugField (auto-generated)
- [ ] `content` TextField (rich text)
- [ ] `excerpt` TextField
- [ ] `featured_image` ImageField
- [ ] `category` ForeignKey to BlogCategory
- [ ] `tags` ManyToManyField to BlogTag
- [ ] `is_published` BooleanField (default=False)
- [ ] `published_at` DateTimeField
- [ ] `views_count` IntegerField (default=0)
- [ ] `created_at` timestamp
- [ ] `updated_at` timestamp
- [ ] Method to increment views

Create BlogCategory model:
- [ ] `name` CharField
- [ ] `slug` SlugField

Create BlogTag model:
- [ ] `name` CharField
- [ ] `slug` SlugField

### 10.2 Blog Views
**File:** `blog/views.py`

- [ ] `BlogListView` (GET) - List published posts
  - Pagination
  - Filter by category/tag
  
- [ ] `BlogDetailView` (GET) - Single post view
  - Increment views
  - Show related posts
  
- [ ] `BlogCreateView` (GET/POST) - Create post (admin only)
- [ ] `BlogUpdateView` (GET/POST) - Edit post (admin only)
- [ ] `BlogDeleteView` (POST) - Delete post (admin only)

### 10.3 Blog Forms
**File:** `blog/forms.py`

- [ ] `BlogPostForm` - All blog fields with rich text editor

### 10.4 Blog Templates
**Directory:** `templates/blog/`

- [ ] `blog_list.html` - Blog listing
- [ ] `blog_detail.html` - Single post view
- [ ] `blog_form.html` - Create/edit post
- [ ] Partials:
  - [ ] `_blog_card.html` (with featured image)
  - [ ] `_recent_posts.html` (for homepage)

---

## Phase 11: Static Pages & Landing

### 11.1 Landing Page
**File:** `core/views.py`

Create HomeView:
- [ ] Hero section with CTA button
  - If logged in: redirect to explore page
  - If not logged in: redirect to login page
- [ ] Recent blog posts section (3-4 posts)
  - Include featured images
  - Link to full blog
- [ ] Features overview
- [ ] Statistics counter (interns, employers, internships)

### 11.2 Static Page Views
**File:** `core/views.py`

- [ ] `AboutView` (GET) - About page
- [ ] `ContactView` (GET/POST) - Contact form
  - Send email to admin
  - Confirmation email to user

### 11.3 Static Templates
**Directory:** `templates/core/static/`

- [ ] `home.html` - Landing page
- [ ] `about.html` - About page
- [ ] `contact.html` - Contact page

---

## Phase 12: Error Handling

### 12.1 Error Pages
**Directory:** `templates/errors/`

- [ ] `404.html` - Page not found
- [ ] `400.html` - Bad request
- [ ] `500.html` - Server error
- [ ] `403.html` - Forbidden

### 12.2 Error Handlers
**File:** `lwazi_blue/urls.py`

- [ ] Configure handler404
- [ ] Configure handler400
- [ ] Configure handler500
- [ ] Configure handler403

---

## Phase 13: Email System

### 13.1 Email Configuration
**File:** `lwazi_blue/settings.py`

Configure email settings:
- [ ] Development: Console backend
- [ ] Production: SMTP backend
- [ ] Set DEFAULT_FROM_EMAIL
- [ ] Configure email templates directory

### 13.2 Email Templates
**Directory:** `templates/emails/`

Create HTML email templates:
- [ ] `base_email.html` - Base template with header/footer
- [ ] `welcome.html` - Welcome email
- [ ] `otp_confirmation.html` - Email confirmation OTP
- [ ] `otp_login.html` - Login OTP
- [ ] `application_submitted.html` - Application confirmation
- [ ] `application_status_update.html` - Status change notification
- [ ] `new_message.html` - New message notification
- [ ] `matched_internship.html` - New matched internship
- [ ] `contact_form.html` - Contact form submission

### 13.3 Email Service
**File:** `core/services/email_service.py`

Create EmailService class:
- [ ] Method: `send_templated_email(template, context, to_email, subject)`
- [ ] Method: `send_bulk_email(template, contexts, to_emails, subject)`
- [ ] Wrapper methods for each email type
- [ ] Check user preferences before sending

---

## Phase 14: Management Commands

### 14.1 User Population Command
**File:** `accounts/management/commands/populate_users.py`

- [ ] Create command with options:
  - `--employers` (number of employers to create)
  - `--interns` (number of interns to create)
- [ ] Generate realistic fake data using Faker
- [ ] Create complete profiles
- [ ] Set password to 'password123' for all
- [ ] Create skills, industries, locations

### 14.2 Internship Population Command
**File:** `core/management/commands/populate_posts.py`

- [ ] Create command with `--posts` option
- [ ] Generate realistic internship postings
- [ ] Assign to random employers
- [ ] Set realistic dates and requirements

### 14.3 Blog Population Command
**File:** `blog/management/commands/populate_blog.py`

- [ ] Create command with `--posts` option
- [ ] Generate blog posts with categories and tags
- [ ] Set random publish dates
- [ ] Assign to admin users

---

## Phase 15: Admin Interface

### 15.1 Admin Configuration
Register models in admin:

**File:** `accounts/admin.py`
- [ ] CustomUser
- [ ] OTPToken

**File:** `core/admin.py`
- [ ] InternProfile
- [ ] EmployerProfile
- [ ] InternDocument
- [ ] Education
- [ ] WorkExperience
- [ ] InternshipPost
- [ ] Skill
- [ ] Industry
- [ ] Location
- [ ] Conversation
- [ ] Message

**File:** `applications/admin.py`
- [ ] Application

**File:** `blog/admin.py`
- [ ] BlogPost
- [ ] BlogCategory
- [ ] BlogTag

**File:** `notifications/admin.py`
- [ ] Notification
- [ ] NotificationPreference

### 15.2 Admin Customization
- [ ] List display fields for each model
- [ ] List filters
- [ ] Search fields
- [ ] Inline editing where appropriate
- [ ] Custom actions (bulk status updates, etc.)

---

## Phase 16: Frontend & UI

### 16.1 Base Templates
**Directory:** `templates/`

- [ ] `base.html` - Base template with:
  - Bootstrap 5 CSS/JS
  - Custom CSS file
  - jQuery for AJAX
  - Navigation include
  - Footer include
  - Messages display
  - Block content area
  
- [ ] `includes/navbar.html` - Conditional navigation
- [ ] `includes/footer.html` - Footer with links
- [ ] `includes/messages.html` - Django messages display

### 16.2 Static Files
**Directory:** `static/`

Create CSS files:
- [ ] `css/main.css` - Main stylesheet
- [ ] `css/dashboard.css` - Dashboard styles
- [ ] `css/profile.css` - Profile page styles
- [ ] `css/messaging.css` - Chat interface styles

Create JavaScript files:
- [ ] `js/main.js` - Global JavaScript
- [ ] `js/notifications.js` - Notification handling
- [ ] `js/messaging.js` - Real-time messaging
- [ ] `js/search.js` - Search and filter
- [ ] `js/forms.js` - Form validation and AJAX

### 16.3 Responsive Design
- [ ] Ensure all pages work on mobile
- [ ] Test on tablet sizes
- [ ] Implement responsive navigation (hamburger menu)
- [ ] Responsive tables (scroll or stack)
- [ ] Touch-friendly buttons and links

### 16.4 UI Components
Create reusable components:
- [ ] Card components for listings
- [ ] Badge components for status
- [ ] Modal components
- [ ] Form styling
- [ ] Button variations
- [ ] Avatar/profile image handling with fallbacks
- [ ] Loading spinners
- [ ] Empty state messages

### 16.5 Django Template Best Practices
Common pitfalls and solutions:

**Custom Template Filters:**
- [ ] Django doesn't support dictionary access with variable keys: `{{ dict.variable_key }}`
- [ ] Solution: Create custom filters in `app/templatetags/` directory
- [ ] Example: `get_item` filter for dictionary access
- [ ] Always create `__init__.py` in templatetags directory
- [ ] Load filters in templates: `{% load app_filters %}`

**Context Data:**
- [ ] Pass both data dictionaries AND choice tuples to templates
- [ ] Example: Pass `status_counts` (dict) AND `status_choices` (list of tuples)
- [ ] Iterate over tuples, access counts via custom filter

**Province Fields:**
- [ ] Always use PROVINCE_CHOICES for consistent province selection
- [ ] Apply to: InternProfile, EmployerProfile, InternshipPost
- [ ] Use abbreviated codes (GP, WC, KZN) as values, full names as display

**UX Enhancements:**
- [ ] Use Bootstrap tabs for complex forms (e.g., profile pages) to improve organization
- [ ] Convert multi-select fields to toggle badges for better mobile experience
- [ ] Display persistent information (like notes) in cards, not dismissible alerts
- [ ] Sync navigation elements (sidebar + tabs) with JavaScript for seamless UX

**Common Template Patterns:**
```django
{# Loading custom filters #}
{% load app_filters %}

{# Iterating over choices while accessing counts #}
{% for status_code, status_name in status_choices %}
    {{ status_name }}: {{ status_counts|get_item:status_code|default:0 }}
{% endfor %}

{# Safe attribute access #}
{{ object.attribute|default:"Not set" }}

{# URL parameter preservation #}
<a href="?page={{ num }}{% if filter %}&filter={{ filter }}{% endif %}">

{# INVALID: Cannot pass arguments to methods #}
{% if conversation.get_unread_count user > 0 %}  {# This will fail! #}

{# VALID: Pre-calculate in view #}
{% if conversation.unread_count > 0 %}  {# This works! #}
```

**Template Organization:**
- [ ] Use template inheritance (extends/blocks)
- [ ] Create reusable partials in `templates/includes/`
- [ ] Load static files: `{% load static %}`
- [ ] Use named URL patterns: `{% url 'app:view_name' %}`
- [ ] Never hardcode URLs in templates

---

## Phase 17: Search & Filter System

### 17.1 Search Functionality
**File:** `core/services/search.py`

Create SearchService class:
- [ ] Method: `search_internships(query, filters)`
  - Full-text search in title, description
  - Filter by skills, industry, location, etc.
  - Date range filtering
  - Return QuerySet
  
- [ ] Method: `search_interns(query, filters)`
  - Search by skills, qualifications
  - Filter by location, experience level
  - Return QuerySet

### 17.2 Filter Forms
**File:** `core/forms.py`

- [ ] `InternshipFilterForm` - Skills, industry, location, date range
- [ ] `InternFilterForm` - Skills, location, qualification level

### 17.3 AJAX Implementation
- [ ] Live search (debounced)
- [ ] Filter updates without page reload
- [ ] Pagination with AJAX
- [ ] URL parameter persistence

---

## Phase 18: Testing

### 18.1 Unit Tests
Create test files for each app:

**accounts/tests.py:**
- [ ] Test user registration
- [ ] Test login with credentials
- [ ] Test OTP generation and validation
- [ ] Test email confirmation flow
- [ ] Test OTP login

**core/tests.py:**
- [ ] Test profile creation and updates
- [ ] Test document uploads
- [ ] Test internship CRUD operations
- [ ] Test matching algorithm
- [ ] Test messaging system

**applications/tests.py:**
- [ ] Test application submission
- [ ] Test status updates
- [ ] Test duplicate application prevention

**blog/tests.py:**
- [ ] Test blog post creation
- [ ] Test blog listing and filtering

**notifications/tests.py:**
- [ ] Test notification creation
- [ ] Test preference checking
- [ ] Test email sending

### 18.2 Integration Tests
- [ ] Test full application workflow
- [ ] Test messaging workflow
- [ ] Test notification workflow
- [ ] Test search and matching

### 18.3 Manual Testing Checklist
- [ ] Test all user flows
- [ ] Test email notifications
- [ ] Test responsive design
- [ ] Test browser compatibility
- [ ] Test form validations
- [ ] Test file uploads
- [ ] Test permission restrictions

---

## Phase 19: Security & Performance

### 19.1 Security Implementation
- [ ] CSRF protection on all forms
- [ ] XSS prevention (template escaping)
- [ ] SQL injection prevention (use ORM)
- [ ] File upload validation (type, size)
- [ ] Rate limiting on login/OTP requests
- [ ] Secure password reset flow
- [ ] HTTPS enforcement in production
- [ ] Security headers (X-Frame-Options, etc.)
- [ ] User permission decorators (@login_required, etc.)

### 19.2 Performance Optimization
- [ ] Database query optimization:
  - Use select_related for ForeignKey
  - Use prefetch_related for ManyToMany
  - Add database indexes
  - Optimize matching algorithm queries
  
- [ ] Caching strategy:
  - Cache homepage content
  - Cache blog listings
  - Cache matching results (short TTL)
  - Cache user profile completion percentage
  
- [ ] Static file optimization:
  - Minify CSS/JS for production
  - Compress images
  - Use CDN for Bootstrap/jQuery
  - Enable gzip compression
  
- [ ] Pagination on all listings
- [ ] Lazy loading for images
- [ ] AJAX for infinite scroll (optional)

---

## Phase 20: Deployment Preparation

### 20.1 Production Settings
**File:** `lwazi_blue/settings_prod.py`

- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use environment variables for secrets
- [ ] Configure production database (PostgreSQL)
- [ ] Set up static files (collectstatic)
- [ ] Configure media files storage
- [ ] Set up SMTP email backend
- [ ] Configure logging

### 20.2 Environment Variables
Create `.env.example`:
- [ ] SECRET_KEY
- [ ] DATABASE_URL
- [ ] EMAIL_HOST
- [ ] EMAIL_PORT
- [ ] EMAIL_HOST_USER
- [ ] EMAIL_HOST_PASSWORD
- [ ] ALLOWED_HOSTS

### 20.3 Deployment Files
- [ ] `requirements.txt` - All dependencies with versions
- [ ] `runtime.txt` - Python version
- [ ] `Procfile` - For Heroku/similar platforms
- [ ] `wsgi.py` - Production WSGI configuration
- [ ] `.gitignore` - Exclude sensitive files

### 20.4 Database Migration
- [ ] Export local data (if needed)
- [ ] Run migrations on production
- [ ] Import initial data
- [ ] Create production superuser

### 20.5 Server Configuration
- [ ] Set up web server (Nginx/Apache)
- [ ] Configure WSGI server (Gunicorn/uWSGI)
- [ ] Set up SSL certificate
- [ ] Configure firewall
- [ ] Set up backup schedule
- [ ] Configure monitoring

---

## Phase 21: Documentation

### 21.1 README.md
- [ ] Project description
- [ ] Features list
- [ ] Installation instructions
- [ ] Configuration guide
- [ ] Usage examples
- [ ] Testing credentials
- [ ] Technologies used
- [ ] License information

### 21.2 API Documentation (if applicable)
- [ ] Document AJAX endpoints
- [ ] Request/response examples
- [ ] Authentication requirements

### 21.3 User Documentation
- [ ] User guide for interns
- [ ] User guide for employers
- [ ] Admin guide
- [ ] FAQ section

---

## Phase 22: Post-Launch

### 22.1 Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Set up analytics (Google Analytics)
- [ ] Monitor server resources
- [ ] Monitor email delivery rates

### 22.2 Maintenance Tasks
- [ ] Regular database backups
- [ ] Log rotation
- [ ] Security updates
- [ ] Dependency updates
- [ ] Clean up old OTP tokens
- [ ] Archive old applications

### 22.3 Future Enhancements
- [ ] Video CV uploads
- [ ] Real-time chat (WebSockets)
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics dashboard
- [ ] Interview scheduling system
- [ ] Skills assessment tests
- [ ] Recommendation system improvements
- [ ] Multi-language support

---

## URL Structure

### Main URLs (`lwazi_blue/urls.py`)
```
/                           -> Home page
/about/                     -> About page
/contact/                   -> Contact page

/accounts/register/         -> Registration
/accounts/login/            -> Login
/accounts/logout/           -> Logout
/accounts/otp-login/        -> OTP login
/accounts/email-confirmation/ -> Email confirmation

/dashboard/                 -> User dashboard (route by type)

/profile/                   -> View/edit profile
/profile/<user_id>/         -> Public profile view

/internships/               -> Browse internships
/internships/<id>/          -> Internship detail
/internships/create/        -> Create internship
/internships/<id>/edit/     -> Edit internship
/internships/my-posts/      -> Employer's internships

/interns/                   -> Browse interns (employer only)
/interns/<id>/              -> Intern public profile

/explore/                   -> Matched listings (route by type)

/applications/              -> My applications
/applications/<id>/         -> Application detail
/applications/create/<internship_id>/ -> Apply
/applications/<id>/update-status/ -> Update application status

/messages/                  -> Conversations list
/messages/<conversation_id>/ -> Conversation detail
/messages/start/<intern_id>/ -> Start conversation

/notifications/             -> Notifications list
/notifications/settings/    -> Notification preferences

/blog/                      -> Blog listing
/blog/<slug>/               -> Blog post detail
/blog/create/               -> Create blog post (admin)
/blog/<slug>/edit/          -> Edit blog post (admin)

/admin/                     -> Django admin
```

---

## Database Schema Summary

### accounts app
- CustomUser
- OTPToken

### core app
- InternProfile
- EmployerProfile
- Skill
- Industry
- Location
- InternDocument
- Education
- WorkExperience
- InternshipPost
- Conversation
- Message

### applications app
- Application

### blog app
- BlogPost
- BlogCategory
- BlogTag

### notifications app
- Notification
- NotificationPreference

---

## Technology Stack

### Backend
- Django 4.2+
- Python 3.10+
- SQLite (development) / PostgreSQL (production)

### Frontend
- Bootstrap 5
- jQuery
- HTML5/CSS3
- JavaScript (ES6+)

### Libraries
- Pillow (image processing)
- django-crispy-forms (form rendering)
- Faker (mock data generation)
- python-dotenv (environment variables)

### Deployment
- Gunicorn (WSGI server)
- Nginx (web server)
- PostgreSQL (database)
- Redis (caching, optional)

---

## Development Workflow

### 1. Setup Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Populate mock data
python manage.py populate_users --employers 10 --interns 50
python manage.py populate_posts --posts 20
python manage.py populate_blog --posts 10

# Run development server
python manage.py runserver
```

### 2. Git Workflow
- Create feature branches for each phase
- Regular commits with descriptive messages
- Pull request reviews before merging
- Keep main branch stable

### 3. Testing Workflow
- Write tests alongside features
- Run tests before commits
- Maintain >80% code coverage
- Manual testing checklist before deployment

### 4. Common Issues & Troubleshooting

**TemplateSyntaxError: Invalid filter**
- **Issue:** `Invalid filter: 'get_item'` or similar
- **Cause:** Missing custom template filter
- **Solution:** 
  1. Create `app/templatetags/` directory
  2. Add `__init__.py` file (can be empty)
  3. Create filter file (e.g., `app_filters.py`)
  4. Register filter with `@register.filter(name='filter_name')`
  5. Load in template: `{% load app_filters %}`

**TemplateSyntaxError: Unused variable at end of if expression**
- **Issue:** `Unused 'user' at end of if expression` or `{% if object.method variable %}`
- **Cause:** Django templates don't support passing arguments to methods in if statements
- **Solution:**
  1. Calculate the value in the view before rendering
  2. Attach it to the object: `object.computed_value = object.method(arg)`
  3. Use in template: `{% if object.computed_value > 0 %}`
- **Example:**
  ```python
  # In view
  for conversation in conversations:
      conversation.unread_count = conversation.get_unread_count(user)
  
  # In template
  {% if conversation.unread_count > 0 %}
  ```

**Template Not Found**
- **Issue:** `TemplateDoesNotExist`
- **Solution:** 
  1. Check `TEMPLATES` setting in settings.py
  2. Ensure `'APP_DIRS': True` is set
  3. Verify template path matches directory structure
  4. Check template name in render() call

**Static Files Not Loading**
- **Issue:** CSS/JS/images not appearing
- **Solution:**
  1. Run `python manage.py collectstatic` for production
  2. Add `{% load static %}` at top of template
  3. Use `{% static 'path/to/file' %}` for file paths
  4. Check `STATIC_URL` and `STATICFILES_DIRS` in settings.py

**Migration Issues**
- **Issue:** Migration conflicts or errors
- **Solution:**
  1. Delete migration files (keep __init__.py)
  2. Delete database (backup first if needed)
  3. Run `python manage.py makemigrations`
  4. Run `python manage.py migrate`

**Context Variable Not Available**
- **Issue:** Template variable is empty/undefined
- **Solution:**
  1. Print context in view to verify data
  2. Check context dictionary keys match template usage
  3. Verify queryset is evaluated (not lazy)
  4. Use `{{ variable|default:"fallback" }}` for safety

**Import Errors**
- **Issue:** `ModuleNotFoundError` or `ImportError`
- **Solution:**
  1. Verify virtual environment is activated
  2. Check app is in `INSTALLED_APPS`
  3. Ensure `__init__.py` exists in package directories
  4. Reinstall dependencies: `pip install -r requirements.txt`

---

## Success Criteria

### Functionality
- [ ] All features from requirements implemented
- [ ] Matching algorithm returns relevant results
- [ ] Email notifications delivered successfully
- [ ] Messaging system works smoothly
- [ ] Application workflow complete
- [ ] All forms validate properly

### Performance
- [ ] Pages load in <2 seconds
- [ ] Database queries optimized
- [ ] File uploads handled efficiently
- [ ] Search returns results quickly

### Security
- [ ] No security vulnerabilities
- [ ] User data protected
- [ ] File uploads validated
- [ ] Permissions enforced correctly

### User Experience
- [ ] Intuitive navigation
- [ ] Responsive on all devices
- [ ] Clear error messages
- [ ] Helpful feedback to users
- [ ] Accessible to users with disabilities

### Code Quality
- [ ] Code follows PEP 8 standards
- [ ] Proper documentation
- [ ] DRY principle applied
- [ ] Reusable components
- [ ] Clean git history

---

## Estimated Timeline

- **Phase 1-2:** Project Setup & Authentication (1 week)
- **Phase 3-4:** Profile & Internship Management (1.5 weeks)
- **Phase 5-6:** Matching & Applications (1 week)
- **Phase 7-9:** Messaging, Dashboard & Notifications (1.5 weeks)
- **Phase 10-11:** Blog & Static Pages (1 week)
- **Phase 12-14:** Error Handling, Emails & Commands (1 week)
- **Phase 15-17:** Admin, Frontend & Search (1.5 weeks)
- **Phase 18-19:** Testing & Security (1 week)
- **Phase 20-21:** Deployment & Documentation (1 week)
- **Phase 22:** Post-Launch (ongoing)

**Total Estimated Time:** 10-12 weeks for full implementation

---

## Notes

- Use Django's built-in features wherever possible except email, use smtp library instead of django's email service.
- Keep code modular and reusable
- Document complex algorithms and business logic
- Regular backups during development
- Test thoroughly before moving to production
- Gather user feedback for continuous improvement
- Use the provided logo image at C:\Users\Dell\Documents\Projects\Operations\Lwazi Blue\v_1_0\logo.jpg
for top-left logo display.
---

## Contact & Support

For questions or issues during implementation:
- Review Django documentation
- Check project requirements
- Test incrementally
- Document decisions and changes

---

*This implementation plan is a living document and should be updated as the project evolves.*

## Additional Work
----
All previous items have been implemented:
- ✅ Tabbed interface for profile sections
- ✅ Province field with proper choices
- ✅ Toggle badges for multi-select fields (locations, skills, industries)
- ✅ Persistent internal notes display

See Phase 3.6 (Profile Templates) and Phase 6.4 (Application Templates) for implementation details.
----
