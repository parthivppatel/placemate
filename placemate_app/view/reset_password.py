from django.shortcuts import render, redirect
from django.contrib import messages

from ..utils.auth_utils import reset_user_password, validate_reset_token

def reset_password(request):
    """Handles password reset after verifying the reset token."""
    if request.method == "POST":
        new_password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm-password", "").strip()
        reset_token = request.COOKIES.get("reset_token")

        if not reset_token:
            messages.error(request, "Reset session expired. Request a new password reset link.")
            return redirect("forgot-password")

        payload, error = validate_reset_token(reset_token)
        if error:
            messages.error(request, error)
            return redirect("forgot-password")

        if not new_password or not confirm_password:
            messages.error(request, "Both password fields are required.")
            return render(request, "reset_password.html")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "reset_password.html")

        user, message = reset_user_password(payload["email"], new_password)
        if not user:
            messages.error(request, message)
            return redirect("forgot-password")

        messages.success(request, message)
        response = redirect("login")
        response.delete_cookie("reset_token")  
        return response

    return render(request, "reset_password.html")
