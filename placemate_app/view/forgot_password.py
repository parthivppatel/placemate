import datetime
import random
import jwt
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils.html import escape

from placemate import settings

from ..schema.users import User

def generate_otp():
    return str(random.randint(100000, 999999))

def generate_otp_token(email, otp):
    payload = {
        "email": email,
        "otp": otp,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=60),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Please enter your registered email.")
            return render(request, "forgot_password.html")

        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not registered.")
            return render(request, "forgot_password.html")
        
        otp = generate_otp()
        otp_token = generate_otp_token(email, otp)

        email_subject = "Password Reset OTP - Placemate"
        email_body = f"""
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

        send_mail(
            email_subject,
            "",  
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=email_body,  
        )


        respone = redirect('verify-otp')
        respone.set_cookie("otp_token", otp_token, httponly=True, secure=True)

        return respone

    return render(request, "forgot_password.html")

def generate_reset_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),  
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        otp_token = request.COOKIES.get("otp_token")

        if not otp_token:
            messages.error(request, "OTP expired. Request a new OTP.")
            return redirect("forgot-password")
        
        try:
            payload = jwt.decode(otp_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if datetime.datetime.now(datetime.timezone.utc) > datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc):
                messages.error(request, "OTP expired. Request a new OTP.")
                return redirect("forgot-password")

            correct_otp = payload["otp"]
            email = payload["email"]

            if entered_otp != correct_otp:
                messages.error(request, "Invalid OTP. Try again.")
                return render(request, "verify_otp.html")

            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "Invalid OTP session.")
                return redirect("forgot-password")

            reset_token = generate_reset_token(user.id)

            messages.success(request, "OTP verified successfully! Proceed to reset password.")
            response = redirect("reset-password")
            response.set_cookie("reset_token", reset_token, httponly=True, secure=True)
            response.delete_cookie("otp_token")  
            return response

        except jwt.ExpiredSignatureError:
            messages.error(request, "OTP expired. Request a new OTP.")
        except jwt.InvalidTokenError:
            messages.error(request, "Invalid OTP session.")

        return redirect("forgot-password")

    return render(request, "verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm-password", "").strip()
        reset_token = request.COOKIES.get("reset_token")

        if not reset_token:
            messages.error(request, "Reset session expired. Request a new password reset link.")
            return redirect("forgot-password")
        
        try:
            payload = jwt.decode(reset_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

            if datetime.datetime.now(datetime.timezone.utc) > datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc):
                messages.error(request, "Reset session expired. Request a new password reset link.")
                return redirect("forgot-password")

            if not new_password or not confirm_password:
                messages.error(request, "Both password fields are required.")
                return render(request, "reset_password.html")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "reset_password.html")

            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return render(request, "reset_password.html")

            user_id = payload["user_id"]
            user = User.objects.filter(id=user_id).first()

            if not user:
                messages.error(request, "Invalid reset session. Try again.")
                return redirect("forgot-password")

            user.password = make_password(new_password)
            user.save()

            messages.success(request, "Password reset successfully! You can now log in.")
            response = redirect("login")
            response.delete_cookie("reset_token")  
            return response

        except jwt.ExpiredSignatureError:
            messages.error(request, "Reset session expired. Request a new password reset link.")
        except jwt.InvalidTokenError:
            messages.error(request, "Invalid reset session.")

        return redirect("forgot-password")

    return render(request, "reset_password.html")
