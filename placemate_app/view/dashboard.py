from datetime import timezone
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count

from django.shortcuts import render
from ..decorators import permission_required
from ..utils.jwt_utils import get_user_from_jwt 

from collections import Counter

from ..schema.students import Student  
from ..schema.users import User  
from ..schema.drive_applications import DriveApplication
from ..schema.company_drives import CompanyDrive

def get_students_details(student):
    # Status Breakdown
    application_status = DriveApplication.objects.filter(student=student).values_list('status', flat=True)
    status_counts = Counter(application_status)

    status_data = {
        'Applied': status_counts.get('Applied', 0),
        'Shortlisted': status_counts.get('Shortlisted', 0),
        'Interview': status_counts.get('Interview', 0),
        'Offered': status_counts.get('Offered', 0),
        'Rejected': status_counts.get('Rejected', 0),
    }

    # Drive Participation (last 4 months)
    today = timezone.now()
    four_months_ago = today - timezone.timedelta(days=120)

    drive_data = (
        DriveApplication.objects
        .filter(student=student, created_at__gte=four_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    month_map = {entry['month'].strftime('%b'): entry['count'] for entry in drive_data}

    drive_labels = []
    drive_counts = []

    for i in range(3, -1, -1):
        month = (today - timezone.timedelta(days=30 * i)).strftime('%b')
        drive_labels.append(month)
        drive_counts.append(month_map.get(month, 0))

    eligible_drives = CompanyDrive.objects.filter(end_date__gte=today) 
    eligible_drives_data = []

    for drive in eligible_drives:
        eligible = True
        
        if drive.minimum_cgpa and (student.cgpa or 0) < drive.minimum_cgpa:
            eligible = False
        if drive.tenth and (student.tenth_percentage or 0) < drive.tenth:
            eligible = False
        if drive.twelth and (student.twelfth_percentage or 0) < drive.twelth:
            eligible = False
        
        if eligible:
            eligible_drives_data.append({
                'id': drive.id,
                'company': drive.company.name,
                'role': drive.drive_name, 
                'package': f"{drive.ug_package_min} - {drive.ug_package_max}",  
                'end_date': drive.end_date.strftime('%Y-%m-%d'), 
            })

    student_applications = DriveApplication.objects.filter(student=student)
    application_data = []

    for application in student_applications:
        # Accessing the company name through the related CompanyDrive model
        application_data.append({
            'company': application.drive.company.name,  # Corrected to access the company name
            'drive': application.drive.drive_name,
            'applied_on': application.created_at.strftime('%Y-%m-%d'),
            'status': application.get_status_display(),  # Optionally use get_status_display() for the human-readable status
        })

    return {
        "status_data": status_data,
        "drive_chart": {
            "labels": drive_labels,
            "data": drive_counts
        },
        "eligible_drives": eligible_drives_data,
        "applications": application_data
    }

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

        student_dashboard_details = get_students_details(student)
        page_title = "Welcome, John Doe 👋"
        page_subtitle = "Here's a quick overview of your placement progress"
        return render(request, "student_dashboard.html", {
            "page_title": page_title,
            "page_subtitle": page_subtitle,
            "user_email": user_email,
            "student": student,  
            "profile_name": f"{student.first_name} {student.last_name}",
            "student_dashboard_details": student_dashboard_details,
        })

    elif user_role == "Company":
        return render(request, "company_dashboard.html", {"user_email": user_email})
    elif user_role == "Admin":
        return render(request, "admin_dashboard.html", {"user_email": user_email})
    else:
        return render(request, "error.html", {"error": "Invalid role"})
