from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from .models import CustomUser, OTPToken
from .forms import RegisterForm, LoginForm, OTPRequestForm, OTPLoginForm, EmailConfirmationForm
from core.email_service import send_email


def register(request):
    """
    User registration view
    Creates user with email_confirmed=False and redirects to email confirmation
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create OTP for email confirmation
            otp = OTPToken.create_otp(user, 'email_confirmation')
            
            # Send welcome email with OTP
            send_welcome_email(user, otp)
            
            messages.success(
                request,
                f'Account created successfully! Please check your email ({user.email}) to confirm your account.'
            )
            
            # Redirect to email confirmation page with email parameter
            return redirect(f"{reverse('accounts:email_confirmation')}?email={user.email}")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    User login view
    Checks if email is confirmed before allowing login
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if email is confirmed
            if not user.email_confirmed:
                messages.warning(
                    request,
                    'Please confirm your email before logging in.'
                )
                return redirect(f"{reverse('accounts:email_confirmation')}?email={user.email}")
            
            # Login user
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', 'core:dashboard')
            return redirect(next_page)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


def email_confirmation(request):
    """
    Email confirmation view
    Handles both GET (display form) and POST (verify OTP)
    Also handles auto-confirmation via URL parameters
    """
    email = request.GET.get('email', '')
    otp_param = request.GET.get('otp', '')
    
    # Try to get user by email
    user = None
    if email:
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email address.')
            return redirect('accounts:login')
    
    # Auto-trigger confirmation if both email and OTP are in URL
    if user and otp_param:
        otp = OTPToken.verify_otp(user, otp_param, 'email_confirmation')
        if otp:
            user.confirm_email()
            otp.mark_as_used()
            messages.success(
                request,
                'Email confirmed successfully! You can now log in.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired confirmation link.')
    
    # Check if email is already confirmed (GET request with only email param)
    if user and user.email_confirmed and request.method == 'GET':
        messages.info(
            request,
            'Your email is already confirmed. You can log in now.'
        )
        return render(request, 'accounts/email_confirmation.html', {
            'already_confirmed': True,
            'user': user
        })
    
    # Handle OTP confirmation form submission
    if request.method == 'POST':
        form = EmailConfirmationForm(user, request.POST)
        if form.is_valid():
            user.confirm_email()
            messages.success(
                request,
                'Email confirmed successfully! You can now log in.'
            )
            return redirect('accounts:login')
    else:
        form = EmailConfirmationForm(user)
    
    return render(request, 'accounts/email_confirmation.html', {
        'form': form,
        'email': email,
        'user': user,
        'already_confirmed': False
    })


def otp_login(request):
    """
    OTP-based login view (passwordless authentication)
    Step 1: Request OTP
    Step 2: Verify OTP and login
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    # Check if we're at step 2 (verifying OTP)
    email = request.session.get('otp_login_email', '')
    
    if email and request.method == 'POST':
        # Step 2: Verify OTP
        form = OTPLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            
            # Clear session
            if 'otp_login_email' in request.session:
                del request.session['otp_login_email']
            
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('core:dashboard')
    elif request.method == 'POST':
        # Step 1: Request OTP
        form = OTPRequestForm(request.POST)
        if form.is_valid():
            user = form.user
            
            # Create OTP
            otp = OTPToken.create_otp(user, 'login')
            
            # Send OTP email
            send_otp_login_email(user, otp)
            
            # Store email in session
            request.session['otp_login_email'] = user.email
            
            messages.success(
                request,
                f'OTP sent to {user.email}. Please check your email.'
            )
            
            # Redirect to same page to show OTP input form
            return redirect('accounts:otp_login')
    else:
        if email:
            # Step 2: Show OTP verification form
            form = OTPLoginForm(initial={'email': email})
        else:
            # Step 1: Show email request form
            form = OTPRequestForm()
    
    return render(request, 'accounts/otp_login.html', {
        'form': form,
        'step': 2 if email else 1,
        'email': email
    })


@require_http_methods(["POST"])
def request_otp(request):
    """
    AJAX endpoint to request a new OTP
    Used for resending OTP during email confirmation or OTP login
    """
    email = request.POST.get('email', '')
    otp_type = request.POST.get('otp_type', 'email_confirmation')
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'})
    
    try:
        user = CustomUser.objects.get(email=email)
        
        # Create new OTP
        otp = OTPToken.create_otp(user, otp_type)
        
        # Send email based on type
        if otp_type == 'email_confirmation':
            send_confirmation_email(user, otp)
            message = f'Confirmation code sent to {email}'
        else:  # login
            send_otp_login_email(user, otp)
            message = f'Login code sent to {email}'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'No account found with this email address.'
        })


# Email sending functions

def send_welcome_email(user, otp):
    """Send welcome email with email confirmation OTP"""
    confirmation_link = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://127.0.0.1:8000'}/accounts/email-confirmation/?email={user.email}&otp={otp.otp_code}"
    
    subject = 'Welcome to Lwazi Blue - Confirm Your Email'
    message = f"""
Hello {user.username},

Welcome to Lwazi Blue! We're excited to have you on board.

To complete your registration, please confirm your email address using one of the following methods:

Method 1: Click the link below
{confirmation_link}

Method 2: Enter this code on the confirmation page
Your confirmation code: {otp.otp_code}

This code will expire in 10 minutes.

If you didn't create this account, please ignore this email.

Best regards,
The Lwazi Blue Team
    """
    
    # Send email using custom smtplib service (non-blocking)
    try:
        send_email(user.email, subject, message, message)
    except Exception as e:
        print(f"⚠️  Email sending failed (non-critical): {e}")


def send_confirmation_email(user, otp):
    """Send email confirmation OTP (for resending)"""
    confirmation_link = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://127.0.0.1:8000'}/accounts/email-confirmation/?email={user.email}&otp={otp.otp_code}"
    
    subject = 'Lwazi Blue - Email Confirmation Code'
    message = f"""
Hello {user.username},

Your email confirmation code is: {otp.otp_code}

Or click this link to confirm automatically:
{confirmation_link}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
The Lwazi Blue Team
    """
    
    # Send email using custom smtplib service (non-blocking)
    try:
        send_email(user.email, subject, message, message)
    except Exception as e:
        print(f"⚠️  Email sending failed (non-critical): {e}")


def send_otp_login_email(user, otp):
    """Send OTP for passwordless login"""
    subject = 'Lwazi Blue - Your Login Code'
    message = f"""
Hello {user.username},

Your login code is: {otp.otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email and ensure your account is secure.

Best regards,
The Lwazi Blue Team
    """
    
    # Send email using custom smtplib service (non-blocking)
    try:
        send_email(user.email, subject, message, message)
    except Exception as e:
        print(f"⚠️  Email sending failed (non-critical): {e}")
