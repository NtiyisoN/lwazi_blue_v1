# Lwazi Blue - Graduate Placement Platform

A Django-based platform designed to bridge the gap between unemployed graduates and potential employers in South Africa.

## Features

### For Interns
- Complete profile management with skills, qualifications, work experience, location, industries of interest, and profile photo
- Document uploads (CV, qualifications, academic scripts, other docs) with version control
- Search and filter options for internship opportunities
- Smart matching algorithm that suggests relevant internships based on skills, qualifications, industry, and location
- Application tracking with comprehensive status updates
- Direct messaging (can only respond to employers)
- Dashboard for tracking applications and notifications
- Email notifications for applications and status updates

### For Employers
- Company profile management
- Create and manage internship postings
- Search and filter potential interns based on skills, location, and qualifications
- Smart matching algorithm for finding suitable candidates
- Review and manage applications with multiple status options
- Direct messaging with interns (can initiate conversations)
- Dashboard for tracking posts, applications, and messages
- View intern profiles with photos

### General Features
- User authentication with email confirmation (OTP-based)
- Alternative OTP login (passwordless authentication)
- Blog section for admin/internal users
- Email notifications for all major events
- Responsive Bootstrap 5 UI
- Error pages (404, 400, 403, 500)
- Notification preferences management

## Technology Stack

### Backend
- Django 4.2.8
- Python 3.10+
- SQLite (development) / PostgreSQL (production)

### Frontend
- Bootstrap 5
- jQuery
- HTML5/CSS3
- JavaScript

### Libraries
- Pillow (image processing)
- django-crispy-forms & crispy-bootstrap5 (form rendering)
- Faker (mock data generation)
- python-dotenv (environment variables)

## Installation Instructions

### 1. Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### 2. Clone or Download the Project
```bash
cd "path/to/project/folder"
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables (Optional for Production)
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Populate Mock Data (Optional)
```bash
# Create mock users
python manage.py populate_users --employers 10 --interns 50

# Create mock internship posts
python manage.py populate_posts --posts 20

# Create mock blog posts
python manage.py populate_blog --posts 10
```

### 9. Run Development Server
```bash
python manage.py runserver
```

### 10. Access the Application
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
lwazi_blue/
├── accounts/              # User authentication and custom user model
│   ├── models.py         # CustomUser, OTPToken models
│   ├── views.py          # Authentication views
│   ├── forms.py          # Authentication forms
│   └── urls.py           # Authentication URLs
├── core/                  # Main app with profiles, posts, messages
│   ├── models.py         # InternProfile, EmployerProfile, InternshipPost, etc.
│   ├── views.py          # Core views
│   ├── forms.py          # Core forms
│   └── services/         # Business logic (matching, search, email)
├── applications/          # Application management
│   ├── models.py         # Application model
│   ├── views.py          # Application views
│   └── forms.py          # Application forms
├── blog/                  # Blog functionality
│   ├── models.py         # BlogPost, BlogCategory, BlogTag models
│   ├── views.py          # Blog views
│   └── forms.py          # Blog forms
├── notifications/         # Notification system
│   ├── models.py         # Notification, NotificationPreference models
│   ├── views.py          # Notification views
│   └── services.py       # Notification service
├── templates/             # HTML templates
│   ├── accounts/         # Authentication templates
│   ├── core/             # Core templates
│   ├── applications/     # Application templates
│   ├── blog/             # Blog templates
│   ├── notifications/    # Notification templates
│   ├── emails/           # Email templates
│   ├── errors/           # Error page templates
│   └── includes/         # Reusable template partials
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images and icons
├── media/                 # User-uploaded files
│   ├── profile_photos/   # Intern profile photos
│   ├── documents/        # Intern documents
│   ├── company_logos/    # Employer logos
│   └── blog_images/      # Blog images
├── lwazi_blue/           # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Key Features Implementation

### 1. Matching Algorithm
The platform uses an intelligent matching algorithm with configurable weights:
- Skills match: 40%
- Industry match: 25%
- Location match: 20%
- Qualification level: 15%

Weights can be adjusted in `settings.py` under `MATCHING_WEIGHTS`.

### 2. Document Management
- Interns can upload multiple documents (CV, qualifications, ID, transcripts)
- Version control for document updates
- Old versions are retained but marked as non-latest

### 3. Application Workflow
Application statuses:
- `pending` - Initial submission
- `success` - Application accepted
- `declined` - Application rejected
- `interview_pending` - Interview scheduled
- `interview_success` - Interview passed
- `interview_unsuccess` - Interview failed
- `pending_final_decision` - Awaiting final decision

### 4. Messaging System
- Employers can initiate conversations with interns
- Interns can only reply to employer messages
- Email notifications for new messages
- Unread message indicators

### 5. Email Notifications
Users receive email notifications for:
- Application submissions
- Application status updates
- New messages
- New matched internships
- Deadline reminders

Users can manage notification preferences in their settings.

### 6. Authentication
- Standard username/password authentication
- Email confirmation with OTP (One-Time Password)
- Alternative OTP-based login (passwordless)
- Automatic OTP confirmation via URL parameters

## Development Workflow

### Creating New Features
1. Update models in the appropriate app
2. Create and run migrations
3. Create forms for user input
4. Create views for business logic
5. Create templates for UI
6. Update URLs
7. Add tests
8. Update admin interface

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
```

### Creating Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration SQL
python manage.py sqlmigrate app_name migration_name
```

### Collecting Static Files (Production)
```bash
python manage.py collectstatic
```

## Configuration

### Email Configuration
For development, emails are printed to the console. For production, update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@lwazi-blue.co.za'
```

### Database Configuration
For production, switch to PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lwazi_blue_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Testing Credentials

After running `populate_users`, you can login with:
- **Interns:** `intern1`, `intern2`, etc. (password: `password123`)
- **Employers:** `employer1`, `employer2`, etc. (password: `password123`)
- **Admin:** Use the superuser credentials you created

## Management Commands

### populate_users
Create mock employers and interns:
```bash
python manage.py populate_users --employers 10 --interns 50
```

### populate_posts
Create mock internship posts:
```bash
python manage.py populate_posts --posts 20
```

### populate_blog
Create mock blog posts:
```bash
python manage.py populate_blog --posts 10
```

## Deployment

### Preparation
1. Set `DEBUG = False` in production settings
2. Configure `ALLOWED_HOSTS`
3. Set up production database (PostgreSQL recommended)
4. Configure SMTP email backend
5. Set up static file serving
6. Configure media file storage
7. Set up SSL certificate
8. Configure environment variables

### Production Checklist
- [ ] Update `SECRET_KEY` (use environment variable)
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure SMTP email
- [ ] Run `collectstatic`
- [ ] Set up web server (Nginx/Apache)
- [ ] Configure WSGI server (Gunicorn/uWSGI)
- [ ] Set up SSL certificate
- [ ] Configure firewall
- [ ] Set up backup schedule
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, etc.)

## Troubleshooting

### Common Issues

**Issue:** Migrations fail
**Solution:** Delete migration files (except `__init__.py`), delete `db.sqlite3`, and run migrations again

**Issue:** Static files not loading
**Solution:** Run `python manage.py collectstatic`

**Issue:** Import errors
**Solution:** Make sure virtual environment is activated and dependencies are installed

**Issue:** Email not sending
**Solution:** Check email configuration in `settings.py` and verify SMTP credentials

**Issue:** Permission denied errors
**Solution:** Check file permissions on media and static directories

## Contributing

When contributing to this project:
1. Create a feature branch
2. Write tests for new features
3. Follow PEP 8 style guidelines
4. Update documentation
5. Submit a pull request

## Support

For issues or questions:
- Review the implementation plan in `setup.md`
- Check Django documentation: https://docs.djangoproject.com/
- Review the code comments and docstrings

## License

This project is for educational and demonstration purposes.

## Notes

- Files are stored locally in the `media/` directory
- Email notifications are sent via console backend in development
- All user passwords for mock data are `password123`
- The matching algorithm weights can be adjusted in settings
- Logo image is located at: `logo.jpg` (use for top-left display)

## Next Steps

1. Complete Phase 2: Implement Custom User Model and Authentication
2. Complete Phase 3: Implement Profile Management
3. Complete Phase 4: Implement Internship Posting System
4. Continue with remaining phases as outlined in `setup.md`

---

**Version:** 1.0  
**Last Updated:** November 2025  
**Framework:** Django 4.2.8  
**Python:** 3.10+

