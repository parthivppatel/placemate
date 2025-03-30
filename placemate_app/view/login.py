from django.shortcuts import render,redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages

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

        if not user:
            messages.error(request, "User does not exist.")
            return render(request, 'login.html', {'status': 400})

        if not check_password(password, user.password):
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html', {'status': 401})
        
        user_role = UserRole.objects.filter(user=user).select_related("role").first()
        role_name = user_role.role.name if user_role else "Student"

        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        request.session["user_role"] = role_name

        messages.success(request, f"Welcome, {role_name}!")
        return redirect("/")

    return render(request,'login.html')
