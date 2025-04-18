import os

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from placemate_app.utils.helper_utils import safe_deep_get, safe_value 

from ..schema.students import Student, PlacementStatus
from ..schema.course import Course
from ..schema.cities import City
from ..schema.company_drives import CompanyDrive
from ..schema.users import User

from ..utils.jwt_utils import has_permission, get_user_from_jwt

def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    courses = Course.objects.filter(is_active=True).order_by("name").values("id", "name")

    student_details = {
        "id": student.student_id.id,
        "name": f"{student.first_name} {student.last_name}",
        "email": student.student_id.email,
        "phone": student.student_id.phone,
        "enrollment": student.enrollment,
        "course": student.course.name if student.course else "N/A",
        "batch": f"{student.joining_year} - {student.joining_year + 4}" if student.joining_year else "N/A",
        "joining_year": student.joining_year or "N/A", 
        "cgpa": student.cgpa or "N/A",
        "placement_status": PlacementStatus(student.placement_status).label if student.placement_status is not None else "N/A",
        "graduation_status": student.get_graduation_status_display(),
        "company_placedIn": student.company_placedIn.name if student.company_placedIn else "N/A",
        "package": f"{student.package} LPA" if student.package else "N/A",
        "address": student.address or "N/A",
        "profile": student.profile or "N/A",
        "dob": student.dob.strftime('%Y-%m-%d') if student.dob else "N/A",
        "gender": student.gender if student.gender else "",
        "tenth_percentage": student.tenth_percentage or "N/A",  # Added 10th percentage
        "twelfth_percentage": student.twelfth_percentage or "N/A",  # Added 12th percentage
        "backlog": student.backlog or 0,  # Added backlog count
    }
    
    return render(request, "student_profile.html", {
        "student": student,
        "student_details": student_details,
        "page_title": "Student Profile",
        "page_subtitle": f"Details of {student.first_name} {student.last_name}",
        "courses": courses,
        "allowed_fields_message": "You are allowed to update your phone number, address, profile picture, 10th percentage, and 12th percentage.",
    })


def student_edit_student(request, student_id):
    try:
        student = Student.objects.select_related("student_id").get(student_id=student_id)

        if request.method == "POST":

            data = {key: value.strip() for key, value in request.POST.items()}

            student.student_id.phone = data.get('phone', student.student_id.phone)
            student.address = data.get('address', student.address)
            student.tenth_percentage = float(data.get('tenth_percentage')) if data.get('tenth_percentage') else student.tenth_percentage
            student.twelfth_percentage = float(data.get('twelfth_percentage')) if data.get('twelfth_percentage') else student.twelfth_percentage

            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']

                fs = FileSystemStorage(location=os.path.join('media', 'student_profiles'), base_url='/media/student_profiles/')

                file_extension = os.path.splitext(profile_pic.name)[1] 
                new_filename = f"{student_id}{file_extension}"

                # Remove the old profile picture if it exists
                if student.profile and os.path.exists(os.path.join('media', student.profile)):
                    os.remove(os.path.join('media', student.profile))
                    print(f"Old profile picture removed: {student.profile}")

                # Save the new profile picture
                filename = fs.save(new_filename, profile_pic)

                # Get the file path to store in the database
                file_path = fs.url(filename)  

                # Save the file path in the Student model
                student.profile = file_path
            else:
                print("No profile picture uploaded.")

            student.student_id.save()  
            student.save()  

            # Success message
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("student_profile", student_id=student_id)

        # GET request: Render the edit form
        return render(request, "student_profile.html", {
            "student": student,
            "page_title": "Edit Profile",
            "page_subtitle": f"Edit details of {student.first_name} {student.last_name}",
        })

    except Student.DoesNotExist:
        # Handle case where student does not exist
        messages.error(request, "The requested student does not exist.")
        return redirect("dashboard")

    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect("dashboard")
    
def list_student_drives(request):
    try:
        # Extract and verify the token
        user_payload = get_user_from_jwt(request)
        if not user_payload:
            return JsonResponse({"message": "Invalid or missing token"}, status=401)

        # Extract email from the token payload
        user_email = user_payload.get("email")
        if not user_email:
            return JsonResponse({"message": "Email not found in token"}, status=400)

        # Get the user and student based on the email
        try:
            user = User.objects.get(email=user_email)
            student = Student.objects.get(student_id=user)  # Match the OneToOneField
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)

        # Get the current date
        current_date = timezone.now()

        # Filter company drives that are either scheduled or ongoing
        active_drives = CompanyDrive.objects.filter(
            status__in=["scheduled", "ongoing"]
        ).select_related('company')  # Using select_related to minimize queries

        # Format the drives for the template
        drives_data = []
        for drive in active_drives:
            company = drive.company

            # Get the city using the headquarter_id (City ID)
            try:
                city = City.objects.get(id=company.headquater_id)  # Fetch the City object using the ID
            except City.DoesNotExist:
                city = None  # If the city does not exist, fallback to None

            # Getting the company details and headquarter location
            city_name = city.cityname if city else "Location not specified"
            state_name = safe_deep_get(city, 'state.statename') or "Location not specified"
            country_name = safe_deep_get(city, 'state.country.name') or "Location not specified"

            # Add drive data to the list
            drive_data = {
                "id": drive.id,
                "drive_name": drive.drive_name,
                "company_name": company.name,
                "company_id": company.id.id,  # Using the company ID
                "company_description": company.description,
                "company_logo": f"/media/{company.logo}" if company.logo else "/static/images/default-company-logo.png",
                "job_type": drive.job_type,
                "job_mode": drive.job_mode,
                "ug_package_min": drive.ug_package_min,
                "ug_package_max": drive.ug_package_max,
                "pg_package_min": drive.pg_package_min,
                "pg_package_max": drive.pg_package_max,
                "start_date": drive.start_date.strftime('%Y-%m-%d'),
                "end_date": drive.end_date.strftime('%Y-%m-%d'),
                "status": drive.status,
                "location": {
                    "city": city_name,
                    "state": state_name,
                    "country": country_name
                }
            }
            drives_data.append(drive_data)

        # Render the student drives page with dynamic content
        return render(request, "student_drives.html", {
            "page_title": "Student Drives",
            "page_subtitle": "Your insight hub to track progress of your placement drives.",
            "student_id": student.student_id.id,  # Pass student_id to the template
            "student": student,
            "student_name": f"{student.first_name} {student.last_name}",  # Pass student name
            "profile_name": f"{student.first_name} {student.last_name}",  # Dynamic profile name
            "drives": drives_data,  # Pass the active drives data to the template
        })

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({"message": f"An unexpected error occurred: {str(e)}"}, status=500)
