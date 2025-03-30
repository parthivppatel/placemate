import datetime
import random
import jwt
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.contrib import messages
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

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        print(entered_otp)
        otp_token = request.COOKIES.get("otp_token")

        if not otp_token:
            messages.error(request, "OTP session expired. Request a new OTP.")
            return redirect("forgot-password")
        
        try:
            payload = jwt.decode(otp_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            email = payload["email"]
            correct_otp = payload["otp"]
            print(correct_otp)

            if entered_otp != correct_otp:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, "verify_otp.html")

            response = redirect("reset-password")
            response.set_cookie("email", email, httponly=True, secure=True)
            return response
        except jwt.ExpiredSignatureError:
            messages.error(request, "OTP expired. Request a new one.")
            return redirect("forgot-password")
        except jwt.DecodeError:
            messages.error(request, "Invalid OTP token.")
            return redirect("forgot-password")
    
    return render(request, "verify_otp.html")

def reset_password(request):
    pass