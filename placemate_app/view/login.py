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
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html', {'status': 400})

        user, roles_or_error = authenticate_user(email, password)

        if not user:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html', {'status': 400})
        
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
        # Get data from the AJAX request
        role = request.POST.get("role")
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        print("Role:", role)
        print("Email:", email)
        print("Password:", password)

        # Validate the inputs
        if not role or not email or not password:
            return JsonResponse({"status": 400, "message": "Role, email, and password are required."})

        # Authenticate the user
        user, roles_or_error = authenticate_user(email, password)
        print("User:", user)

        if not user:
            return JsonResponse({"status": 400, "message": "Invalid email or password."})

        # Check if the selected role is valid
        if role not in roles_or_error:
            return JsonResponse({"status": 400, "message": "Invalid role selected."})

        # Set the JWT cookie with the selected role
        response = JsonResponse({"status": 200, "message": "Logged in successfully."})
        response = set_jwt_cookie(response, user, role)
        return response

    return JsonResponse({"status": 400, "message": "Invalid request method."})