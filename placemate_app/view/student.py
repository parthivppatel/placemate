import os

from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from ..utils.helper_utils import safe_deep_get, get_batch_year, safe_value 

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from ..schema.students import Student, PlacementStatus
from ..schema.course import Course
from ..schema.cities import City
from ..schema.company_drives import CompanyDrive
from ..schema.users import User
from ..schema.company_drive_jobs import CompanyDriveJobs
from ..schema.drive_applications import DriveApplication
from ..schema.drive_locations import DriveLocation

from ..utils.jwt_utils import get_user_from_jwt

def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    courses = Course.objects.filter(is_active=True).order_by("name").values("id", "name")
    batch_year = get_batch_year(student)

    student_details = {
        "id": student.student_id.id,
        "name": f"{student.first_name} {student.last_name}",
        "email": student.student_id.email,
        "phone": student.student_id.phone,
        "enrollment": student.enrollment,
        "course": student.course.name if student.course else "N/A",
        "batch": batch_year or "N/A",
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
        "tenth_percentage": student.tenth_percentage or "N/A", 
        "twelfth_percentage": student.twelfth_percentage or "N/A",  
        "backlog": student.backlog or 0,  
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

                # Save the new profile picture
                filename = fs.save(new_filename, profile_pic)

                # Get the file path to store in the database
                file_path = fs.url(filename)  

                # Save the file path in the Student model
                student.profile = file_path
            else:
                pass

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
        user_payload = get_user_from_jwt(request)
        if not user_payload:
            return JsonResponse({"message": "Invalid or missing token"}, status=401)

        user_email = user_payload.get("email")
        if not user_email:
            return JsonResponse({"message": "Email not found in token"}, status=400)

        try:
            user = User.objects.get(email=user_email)
            student = Student.objects.get(student_id=user)  
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)

        batch_year = get_batch_year(student)

        status_filter = request.GET.get('status', '').strip()
        search_query = request.GET.get('search', '').strip()  

        current_date = timezone.now()

        active_drives = CompanyDrive.objects.select_related('company')
        batch_year = get_batch_year(student)  
        
        if batch_year:
            batch_start_year, batch_end_year = map(int, batch_year.split('-'))
            active_drives = active_drives.filter(
                start_date__gte=f"{batch_start_year}-06-01",
                end_date__lte=f"{batch_end_year}-05-31"  
            )
        else:
            pass

        if status_filter == 'scheduled' or not status_filter:
            active_drives = active_drives.filter(status="scheduled", start_date__gt=current_date)
        elif status_filter == 'ongoing':
            active_drives = active_drives.filter(status="ongoing", start_date__lte=current_date, end_date__gte=current_date)
        elif status_filter == 'completed':
            active_drives = active_drives.filter(status="completed", end_date__lt=current_date)
        elif status_filter == 'all_drives':
            active_drives = active_drives.all()

        if search_query:
            active_drives = active_drives.filter(
                Q(company__name__icontains=search_query) |
                Q(drive_name__icontains=search_query) |
                Q(job_type__icontains=search_query)
            )

        drives_data = []
        for drive in active_drives:
            company = drive.company

            try:
                city = City.objects.get(id=company.headquater_id)  
            except City.DoesNotExist:
                city = None  

            city_name = city.cityname if city else "Location not specified"
            state_name = safe_deep_get(city, 'state.statename') or "Location not specified"
            country_name = safe_deep_get(city, 'state.country.name') or "Location not specified"

            drive_data = {
                "id": drive.id,
                "drive_name": drive.drive_name,
                "company_name": company.name,
                "company_id": company.id.id, 
                "company_description": company.description,
                "company_logo": f"/media/{company.logo}" if company.logo else "/static/images/default-company.png",
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

        filter_options = {
            "statuses": [
                {"value": "scheduled", "label": "Scheduled"},
                {"value": "ongoing", "label": "Ongoing"},
                {"value": "completed", "label": "Completed"}
            ]
        }

        return render(request, "student_drives.html", {
            "page_title": "Student Drives",
            "page_subtitle": "Your insight hub to track progress of your placement drives.",
            "student_id": student.student_id.id,  
            "student": student,
            "student_name": f"{student.first_name} {student.last_name}", 
            "profile_name": f"{student.first_name} {student.last_name}",  
            "drives": drives_data,  
            "filter_options": filter_options,  
        })

    except Exception as e:
        return JsonResponse({"message": f"An unexpected error occurred: {str(e)}"}, status=500)


def student_drive_details(request, drive_id):
    try:
        # ─── 1) AUTH & STUDENT LOOKUP ────────────────────────────────────────────────
        user_payload = get_user_from_jwt(request)
        if not user_payload:
            return JsonResponse({"message": "Invalid or missing token"}, status=401)

        user_email = user_payload.get("email")
        if not user_email:
            return JsonResponse({"message": "Email not found in token"}, status=400)

        try:
            user = User.objects.get(email=user_email)
            student = Student.objects.get(student_id=user)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)

        # ─── 2) FETCH DRIVE & JOBS ──────────────────────────────────────────────────
        drive = get_object_or_404(
            CompanyDrive.objects.select_related("company"),
            id=drive_id
        )
        jobs = CompanyDriveJobs.objects.filter(company_drive=drive)

        # ─── 3) COMPANY & LOCATION CONTEXT ─────────────────────────────────────────
        company = drive.company
        logo_url = company.logo.url if company.logo else "/static/images/default-company.png"
        drive_locations = DriveLocation.objects.filter(drive=drive).select_related("city__state__country")

        location_list = []
        if drive_locations.exists():
            for loc in drive_locations:
                city = loc.city
                location_list.append({
                    "city": city.cityname,
                    "state": safe_deep_get(city, "state.statename") or "Location not specified",
                    "country": safe_deep_get(city, "state.country.name") or "Location not specified"
                })
        else:
            location_list.append({
                "city": "Location not specified",
                "state": "Location not specified",
                "country": "Location not specified"
            })

        # ─── 4) ELIGIBILITY CHECK ─────────────────────────────────────────────────
        now = timezone.now()
        eligible = True
        if drive.minimum_cgpa and (student.cgpa or 0) < drive.minimum_cgpa:
            eligible = False
        if drive.tenth and (student.tenth_percentage or 0) < drive.tenth:
            eligible = False
        if drive.twelth and (student.twelfth_percentage or 0) < drive.twelth:
            eligible = False
        # add additional academic checks here if needed...

        # ─── 5) APPLICATION STATE ───────────────────────────────────────────────────
        application = DriveApplication.objects.filter(
            student=student,
            drive=drive
        ).first()
        applied = bool(application)
        # use the application’s resume_link if they applied, otherwise default to an empty string
        resume_url = application.resume_link if application else ""

        # ─── 6) HANDLE POST ACTIONS ────────────────────────────────────────────────
        if request.method == "POST":
            action = request.POST.get("action")

            # ---- Opt‑In (Submit Resume & Apply) ----
            if action == "opt_in":
                link = request.POST.get("resume_link", "").strip()
                if not link:
                    messages.error(request, "Resume link is required.")
                else:
                    validator = URLValidator()
                    try:
                        validator(link)

                        # If the student has already applied, update the existing DriveApplication
                        if applied:
                            drive_application = DriveApplication.objects.get(student=student, drive=drive)
                            drive_application.resume_link = link
                            drive_application.save(update_fields=["resume_link"])
                            messages.success(request, "Resume link updated.")
                        else:
                            # Create a new DriveApplication if the student hasn't applied yet
                            DriveApplication.objects.create(
                                student=student,
                                drive=drive,
                                resume_link=link
                            )
                            messages.success(request, "Resume link submitted and application created.")
                        
                        resume_url = link  # Store the valid URL

                    except ValidationError:
                        messages.error(request, "Please enter a valid URL.")

            return redirect("student_drive_details", drive_id=drive.id)

        # ─── 7) ADD ADDITIONAL INFO TO CONTEXT ───────────────────────────────────
        # Add the new details to the context
        job_details = {
            "drive_name": drive.drive_name,
            "ctc": {
                "min": drive.ug_package_min,
                "max": drive.ug_package_max
            },
            "job_type": drive.job_type,  # Fetching from the drive model
            "job_mode": drive.job_mode,  # Fetching from the drive model
            "stipend": drive.stipend if drive.stipend else "Not Provided",  # Fetching stipend from the drive model
            "jobs": []  # Empty list to hold multiple jobs
        }

        # Loop through the jobs for this specific drive and add each job's details
        for job in jobs:
            job_details["jobs"].append({
                "job_title": job.job_title,
                "job_description": job.job_description
            })

        # ─── 8) CHECK IF DRIVE IS COMPLETED OR ONGOING ───────────────────────────
        # Check if the drive's end date has passed
        if drive.start_date > now:
            drive_status = "Scheduled"
        elif drive.start_date <= now <= drive.end_date:
            drive_status = "Ongoing"
        else:
            drive_status = "Completed"

        # ─── 9) RENDER TEMPLATE ────────────────────────────────────────────────────
        context = {
            "page_title":       drive.drive_name,
            "page_subtitle":    f"{company.name} Placement Drive",
            "student_id":       student.student_id.id,
            "student":          student,
            "profile_name":     f"{student.first_name} {student.last_name}",
            "company":          company,
            "logo_url":         logo_url,
            "location":         location_list,
            "drive":            drive,
            "jobs":             jobs,
            "deadline":         drive.end_date.strftime("%d/%m/%Y"),
            "eligible":         eligible,
            "applied":          applied,
            "resume_url":       resume_url,
            "job_details":      job_details,
            "drive_status":     drive_status  
        }

        return render(request, "student_view_specific_drive.html", context)

    except Exception as e:
        return JsonResponse({"message": f"An unexpected error occurred: {str(e)}"}, status=500)


def student_drives_application(request, student_id):
    # ─── 1) AUTH & STUDENT LOOKUP ────────────────────────────────────────────────
    user_payload = get_user_from_jwt(request)
    if not user_payload:
        return JsonResponse({"message": "Invalid or missing token"}, status=401)

    user_email = user_payload.get("email")
    if not user_email:
        return JsonResponse({"message": "Email not found in token"}, status=400)

    try:
        user = User.objects.get(email=user_email)
        student = get_object_or_404(Student, student_id=student_id)
    except User.DoesNotExist:
        return JsonResponse({"message": "User not found"}, status=404)
    except Student.DoesNotExist:
        return JsonResponse({"message": "Student not found"}, status=404)

    return render(
        request,
        "student_applications_list.html",
        {
            "student_id": student.student_id.id,
            "student": student,
        }
    )
