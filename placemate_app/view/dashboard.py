from django.shortcuts import render, redirect 
from ..decorators import permission_required

@permission_required('view_dashboard')
def dashboard(request):
    user_email = request.user_data["email"]
    user_role = request.user_data["role"] 

    return render(request, "dashboard.html", {"user_email": user_email, "user_role": user_role})
