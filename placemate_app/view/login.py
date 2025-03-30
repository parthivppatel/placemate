from django.shortcuts import render,redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages

from ..utils import generate_jwt_token

from ..schema.users import User
from ..schema.user_roles import UserRole

def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html', {'status': 400})

        user = User.objects.filter(email__iexact=email).first()
        print(make_password(password))

        if not user:
            messages.error(request, "User does not exist.")
            return render(request, 'login.html', {'status': 400})

        if not check_password(password, user.password):
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html', {'status': 401})
        
        user_role = UserRole.objects.filter(user=user).select_related("role").first()
        role_name = user_role.role.name if user_role else "Student"

        token = generate_jwt_token(user, role_name)

        respone = redirect("/")
        respone.set_cookie("jwt_token", token, httponly=True, secure=True)

        # messages.success(request, f"Welcome, {role_name}")
        return respone

    return render(request,'login.html')
