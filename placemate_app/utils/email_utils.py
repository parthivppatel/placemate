from django.utils.html import escape
from django.core.mail import send_mail
from placemate import settings

def send_custom_email(email, subject, message, html_message=None):
    """
    Sends an email with both plaintext and HTML versions.
    
    :param email: Recipient email address
    :param subject: Email subject
    :param message: Plain text message (fallback for non-HTML email clients)
    :param html_message: HTML formatted message (optional)
    """
    send_mail(
        subject,
        message,  
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        html_message=html_message or message,  
    )

def send_otp_email(email, otp):
    """
    Sends a password reset OTP email.
    
    :param email: Recipient email address
    :param otp: One-time password
    """
    subject = "Password Reset OTP - Placemate"
    message = (
        f"Dear {email},\n"
        f"Your OTP for password reset is: {otp}\n"
        "This OTP is valid for 1 minute.\n"
        "If you did not request this, please ignore this email."
    )

    html_message = f"""
        <html>
        <body>
            <p>Dear {escape(email)},</p>
            <p>Your OTP for password reset is: <strong>{escape(otp)}</strong></p>
            <p>This OTP is valid for <strong>1 minute</strong>.</p>
            <p>If you did not request this, please ignore this email.</p>
            <br>
            <p>Best Regards,</p>
            <p><strong>Placemate Team</strong></p>
        </body>
        </html>
    """

    send_custom_email(email, subject, message, html_message)

def send_welcome_email(email, username):
    """
    Sends a welcome email to a new user.
    
    :param email: Recipient email address
    :param username: Name of the user
    """
    subject = "Welcome to Placemate!"
    message = f"Hello {username},\nWelcome to Placemate! We're excited to have you on board."

    html_message = f"""
        <html>
        <body>
            <p>Hello {escape(username)},</p>
            <p>Welcome to <strong>Placemate</strong>! We're excited to have you on board.</p>
            <br>
            <p>Best Regards,</p>
            <p><strong>Placemate Team</strong></p>
        </body>
        </html>
    """

    send_custom_email(email, subject, message, html_message)