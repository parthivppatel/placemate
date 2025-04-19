from django.shortcuts import render, redirect
from django.contrib import messages

from ..utils.auth_utils import reset_user_password
from ..utils.jwt_utils import get_user_from_jwt

def profile_reset_password(request):    
    user_payload = get_user_from_jwt(request)
    if not user_payload:
        messages.error(request, "You must be logged in to reset your password.")
        return redirect("login")

    if request.method == "POST":
        new_password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm-password", "").strip()

        if not new_password or not confirm_password:
            messages.error(request, "Both password fields are required.")
            return render(request, "profile_reset_password.html")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "profile_reset_password.html")

        user_email = user_payload.get("email")
        user, message = reset_user_password(user_email, new_password)
        if not user:
            messages.error(request, message)
            return redirect("profile_reset_password")

        messages.success(request, "Password updated successfully. Please log in again.")
        response = redirect("login")
        response.delete_cookie("jwt_token")
        return response

    return render(request, "profile_reset_password.html")
