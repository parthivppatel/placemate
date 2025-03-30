from django.shortcuts import render
from ..decorators import permission_required

@permission_required('view_dashboard')
def dashboard(request):
    user_email = request.user_data["email"]
    user_role = request.user_data["role"] 

    print(user_role)

    if user_role == "Student":
        return render(request, "student_dashboard.html", {"user_email": user_email})
    elif user_role == "Company":
        return render(request, "company_dashboard.html", {"user_email": user_email})
    elif user_role == "Admin":
        return render(request, "admin_dashboard.html", {"user_email": user_email})
    else:
        return render(request, "error.html", {"error": "Invalid role"})
