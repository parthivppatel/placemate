from django.shortcuts import render, redirect
from ..utils import decode_jwt_token

def dashboard(request):
    token = request.COOKIES.get("jwt_token")

    if not token:
        return redirect("login")

    payload = decode_jwt_token(token)
    if not payload:
        return redirect("login")

    user_email = payload["email"]
    user_role = payload["role"] 

    return render(request, "dashboard.html", {"user_email": user_email, "user_role": user_role})
