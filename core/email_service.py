"""
Email service using Python's smtplib instead of Django's email backend
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from django.template.loader import render_to_string
from django.conf import settings


class EmailService:
    """
    Custom email service using smtplib
    """
    
    def __init__(self):
        """Initialize email configuration from settings/environment"""
        self.smtp_host = os.getenv('EMAIL_HOST', 'mail.beitsolutions.co.za')
        self.smtp_port = int(os.getenv('EMAIL_PORT', 465))
        self.username = os.getenv('EMAIL_HOST_USER', 'lwazi-blue@beitsolutions.co.za')
        self.password = os.getenv('EMAIL_HOST_PASSWORD', 'zfNAUUWzp}IMTiGa')
        self.from_email = os.getenv('DEFAULT_FROM_EMAIL', 'lwazi-blue@beitsolutions.co.za')
        
        # Auto-detect SSL vs TLS based on port
        if self.smtp_port == 465:
            self.use_ssl = True
            self.use_tls = False
        elif self.smtp_port == 587:
            self.use_ssl = False
            self.use_tls = True
        else:
            # Default to TLS for other ports
            self.use_ssl = False
            self.use_tls = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
        
        # Email notifications can be disabled via settings
        self.enabled = getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', True)
        
        # Development mode - print instead of send
        self.debug_mode = settings.DEBUG
        
        print(f"📧 Email Service Initialized:")
        print(f"   Host: {self.smtp_host}")
        print(f"   Port: {self.smtp_port}")
        print(f"   SSL: {self.use_ssl}, TLS: {self.use_tls}")
        print(f"   Enabled: {self.enabled}")
        print(f"   Debug Mode: {self.debug_mode}")
    
    def send_email(self, to_email, subject, html_content, text_content=None, attachments=None):
        """
        Send an email using smtplib
        
        Args:
            to_email: Recipient email address (string or list)
            subject: Email subject
            html_content: HTML body content
            text_content: Plain text alternative (optional)
            attachments: List of file paths to attach (optional)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Handle list of recipients
            if isinstance(to_email, list):
                recipients = to_email
            else:
                recipients = [to_email]
            
            # Check if email notifications are enabled
            print(f"📧 Email notifications enabled: {self.enabled}")
            if not self.enabled:
                print(f"📧 Email notifications disabled - skipping")
                return True
            
            # Development mode - just print (no SMTP connection)
            print(f"📧 Debug mode: {self.debug_mode}")
            print(f"📧 Username: {self.username}")
            print(f"📧 Password: {self.password}")
            if (not self.username) or (not self.password):
                print(f"📧 username or password is not set - printing email...")
                self._print_email(recipients, subject, html_content, text_content)
                return True
            
            # Create message
            print(f"📧 Creating message...")
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add text content
            if text_content:
                print(f"📧 Adding text content...")
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            print(f"📧 Adding HTML content...")
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if any
            if attachments:
                print(f"📧 Adding attachments...")
                for file_path in attachments:
                    self._attach_file(msg, file_path)
            
            # Send email - use SSL or TLS based on port
            print(f"📧 Sending email...")
            print(f"📧 Use SSL: {self.use_ssl}")
            print(f"📧 Use TLS: {self.use_tls}")
            if self.use_ssl:
                # Port 465 - Use SMTP_SSL (SSL from the start)
                print(f"🔒 Connecting with SMTP_SSL (port 465)...")
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as server:
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                # Port 587 - Use SMTP with STARTTLS
                print(f"🔒 Connecting with SMTP + STARTTLS (port 587)...")
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    if self.use_tls:
                        server.starttls()
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.send_message(msg)
            
            print(f"✅ Email sent to {', '.join(recipients)}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def send_template_email(self, to_email, subject, template_name, context):
        """
        Send an email using a Django template
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Path to email template
            context: Context dictionary for template
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Render HTML content from template
            html_content = render_to_string(template_name, context)
            
            # Generate plain text version (strip HTML tags)
            text_content = self._html_to_text(html_content)
            
            return self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            print(f"❌ Template email failed: {e}")
            return False
    
    def _attach_file(self, msg, file_path):
        """Attach a file to the email message"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            msg.attach(part)
        except Exception as e:
            print(f"⚠️  Failed to attach file {file_path}: {e}")
    
    def _html_to_text(self, html_content):
        """Convert HTML to plain text (simple version)"""
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _print_email(self, recipients, subject, html_content, text_content):
        """Print email to console in development mode"""
        print("\n" + "="*80)
        print("📧 EMAIL (Development Mode - Not Actually Sent)")
        print("="*80)
        print(f"From: {self.from_email}")
        print(f"To: {', '.join(recipients)}")
        print(f"Subject: {subject}")
        print("-"*80)
        if text_content:
            print("Plain Text Content:")
            print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
        else:
            print("HTML Content:")
            print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
        print("="*80 + "\n")


# Singleton instance
_email_service = None

def get_email_service():
    """Get the email service singleton instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


# Convenience functions for common email operations
def send_email(to_email, subject, html_content, text_content=None):
    """Send a simple email"""
    service = get_email_service()
    return service.send_email(to_email, subject, html_content, text_content)


def send_template_email(to_email, subject, template_name, context):
    """Send an email using a template"""
    service = get_email_service()
    return service.send_template_email(to_email, subject, template_name, context)


