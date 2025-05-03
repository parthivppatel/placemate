from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from ..utils import authenticate_user, set_jwt_cookie

def login(request):
    page_title = "Placemate - Login"
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return JsonResponse({"status": 400, "message": "Email and password are required."})

        user, roles_or_error = authenticate_user(email, password)

        if not user:
            return JsonResponse({"status": 400, "message": "Invalid email or password."})
        
        roles = roles_or_error
        if len(roles) == 2:
            return JsonResponse({
                "status": 200,
                "roles": roles,
                "user_id": user.id,
                "email": email,
                "password": password
            })

        response = redirect("/")
        response = set_jwt_cookie(response, user, roles[0])

        return response

    return render(request, 'login.html', {'title': page_title})

def roleloggin(request):
    if request.method == "POST":
        role = request.POST.get("role")
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not role or not email or not password:
            return JsonResponse({"status": 400, "message": "Role, email, and password are required."})

        user, roles_or_error = authenticate_user(email, password)

        if not user:
            return JsonResponse({"status": 400, "message": "Invalid email or password."})

        if role not in roles_or_error:
            return JsonResponse({"status": 400, "message": "Invalid role selected."})

        response = JsonResponse({"status": 200, "message": "Logged in successfully."})
        response = set_jwt_cookie(response, user, role)
        return response

    return JsonResponse({"status": 400, "message": "Invalid request method."})