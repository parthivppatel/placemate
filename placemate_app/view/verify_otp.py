import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from ..utils.otp_utils import decode_otp_token, generate_otp, generate_otp_token
from ..utils.jwt_utils import generate_reset_token
from ..utils.email_utils import send_otp_email

def verify_otp(request):
    """Verifies the OTP entered by the user."""
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        otp_token = request.COOKIES.get("otp_token")

        if not otp_token:
            messages.error(request, "OTP expired. Request a new OTP.")
            return redirect("verify-otp")

        try:
            payload = decode_otp_token(otp_token)
        except ValueError as e:
            # In case the OTP has expired, we explicitly treat it as invalid.
            response = redirect("verify-otp")
            response.delete_cookie("otp_token")  
            messages.error(request, str(e)) 
            return response

        email, correct_otp = payload["email"], payload["otp"]

        if entered_otp != correct_otp:
            messages.error(request, "Invalid OTP. Try again.")
            return render(request, "verify_otp.html")

        reset_token = generate_reset_token(email)

        response = redirect("reset-password")
        response.set_cookie("reset_token", reset_token, httponly=True, secure=False)
        response.delete_cookie("otp_token")  
        return response

    return render(request, "verify_otp.html")

def resend_otp(request):
    """Resends OTP to user's email, only if 30 seconds have passed."""
    otp_token = request.COOKIES.get("otp_token")

    if not otp_token:
        messages.error(request, "OTP session expired. Please restart the process.")
        return redirect("forgot-password")

    try:
        payload = decode_otp_token(otp_token)
    except ValueError as e:
        response = redirect("forgot-password")
        response.delete_cookie("otp_token")  # Clear expired OTP before requesting a new one
        messages.error(request, str(e))  
        return response

    email = payload["email"]
    last_otp_time = request.COOKIES.get("last_otp_time")

    # Enforce 30-second cooldown
    if last_otp_time and time.time() - float(last_otp_time) < 30:
        messages.error(request, "You can only request an OTP resend after 30 seconds.")
        return redirect("verify-otp")

    new_otp = generate_otp()
    new_otp_token = generate_otp_token(email, new_otp)

    send_otp_email(email, new_otp)

    # Update cookies with new OTP and timestamp
    response = redirect("verify-otp")
    response.delete_cookie("otp_token")  # Clear old OTP token before setting a new one
    response.set_cookie("otp_token", new_otp_token, httponly=True, secure=False, max_age=settings.OTP_EXPIRATION_DELTA)
    response.set_cookie("last_otp_time", str(time.time()), httponly=True, secure=False)

    messages.success(request, "A new OTP has been sent to your email.")
    return response
