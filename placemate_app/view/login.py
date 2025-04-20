from django.shortcuts import render, redirect
from django.contrib import messages

from ..utils import authenticate_user, set_jwt_cookie

def login(request):
    page_title = "Placemate - Login"
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html', {'status': 400})

        user, error_message = authenticate_user(email, password)

        if not user:
            messages.error(request, error_message)
            return render(request, 'login.html', {'status': 400})

        response = redirect("/")
        response = set_jwt_cookie(response, user, error_message)

        return response

    return render(request, 'login.html', {'title': page_title})
