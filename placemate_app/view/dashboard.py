from django.shortcuts import render

def dashboard(request):
    user_role = request.session.get("user_role", "Student")  
    return render(request, "dashboard.html", {"role": user_role})