import os

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

from ..schema.students import Student, PlacementStatus, GraduationStatus, Gender, Company
from ..schema.cities import City
from ..schema.course import Course


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