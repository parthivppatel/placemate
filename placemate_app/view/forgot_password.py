from django.shortcuts import render, redirect
from django.contrib import messages

from ..schema.users import User

from ..utils.otp_utils import generate_otp, generate_otp_token
from ..utils.email_utils import send_otp_email

def forgot_password(request):
    """Handles forgot password request."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Please enter your registered email.")
            return render(request, "forgot_password.html")

        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not registered.")
            return render(request, "forgot_password.html")

        # Generate OTP and token
        otp = generate_otp()
        otp_token = generate_otp_token(email, otp)

        # Send OTP email
        send_otp_email(email, otp)

        # Store token in HTTP-only cookie
        response = redirect('verify-otp')
        response.set_cookie("otp_token", otp_token, httponly=True, secure=True)
        return response

    return render(request, "forgot_password.html")
