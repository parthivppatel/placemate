from django.shortcuts import render,redirect
from django.contrib import messages
from ..schema.users import User
from django.contrib.auth.hashers import check_password, make_password

def home(request):
    return redirect('login')

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
        
        
        

    return render(request,'login.html')
