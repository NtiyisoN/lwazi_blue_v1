from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import CustomUser, OTPToken


class RegisterForm(UserCreationForm):
    """
    User registration form with email and user type
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Select your account type'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        """Create user with email_confirmed=False"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        user.email_confirmed = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Custom login form with styled fields
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        """Allow login with email or username"""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with username first
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            
            # If authentication fails, try with email
            if self.user_cache is None:
                try:
                    user = CustomUser.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                except CustomUser.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Invalid username/email or password.',
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class OTPRequestForm(forms.Form):
    """
    Form to request OTP via email
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
    )
    
    def clean_email(self):
        """Validate that email exists"""
        email = self.cleaned_data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            self.user = user
        except CustomUser.DoesNotExist:
            raise forms.ValidationError('No account found with this email address.')
        return email


class OTPLoginForm(forms.Form):
    """
    Form to login with OTP
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'readonly': True
        })
    )
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'autofocus': True,
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        """Validate OTP"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        otp_code = cleaned_data.get('otp_code')
        
        if email and otp_code:
            try:
                user = CustomUser.objects.get(email=email)
                otp = OTPToken.verify_otp(user, otp_code, 'login')
                
                if otp is None:
                    raise forms.ValidationError('Invalid or expired OTP code.')
                
                self.user = user
                # Mark OTP as used
                otp.mark_as_used()
                
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('Invalid email address.')
        
        return cleaned_data


class EmailConfirmationForm(forms.Form):
    """
    Form to confirm email with OTP
    """
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'autofocus': True,
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}'
        }),
        help_text='Enter the 6-digit code sent to your email'
    )
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_otp_code(self):
        """Validate OTP for email confirmation"""
        otp_code = self.cleaned_data.get('otp_code')
        
        if self.user and otp_code:
            otp = OTPToken.verify_otp(self.user, otp_code, 'email_confirmation')
            
            if otp is None:
                raise forms.ValidationError('Invalid or expired OTP code.')
            
            # Mark OTP as used
            otp.mark_as_used()
        
        return otp_code

