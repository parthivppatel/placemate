from django.shortcuts import render
from ..decorators import permission_required
from ..utils.jwt_utils import get_user_from_jwt  
from ..schema.students import Student  
from ..schema.users import User  

@permission_required('view_dashboard')
def dashboard(request):
    # Extract user data from the token
    user_payload = get_user_from_jwt(request)
    if not user_payload:
        return render(request, "error.html", {"error": "Invalid or missing token"})

    user_email = user_payload.get("email")
    user_role = user_payload.get("role")

    if user_role == "Student":
        try:
            user = User.objects.get(email=user_email)
            student = Student.objects.get(student_id=user)
        except User.DoesNotExist:
            return render(request, "403.html", {"error": "User not found"})
        except Student.DoesNotExist:
            return render(request, "403.html", {"error": "Student not found"})

        return render(request, "student_dashboard.html", {
            "user_email": user_email,
            "student": student,  
            "profile_name": f"{student.first_name} {student.last_name}",
        })

    elif user_role == "Company":
        return render(request, "company_dashboard.html", {"user_email": user_email})
    elif user_role == "Admin":
        return render(request, "admin_dashboard.html", {"user_email": user_email})
    else:
        return render(request, "error.html", {"error": "Invalid role"})
