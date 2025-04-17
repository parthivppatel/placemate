import json
from django.contrib.auth.hashers import make_password

from django.utils import timezone 

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from ..decorators import permission_required
from ..schema.users import User
from ..schema.students import Student, PlacementStatus, GraduationStatus, Gender, Company
from ..schema.course import Course
from ..schema.roles import Role
from ..schema.user_roles import UserRole
from ..schema.cities import City
from ..utils.helper_utils import paginate, safe_value,validate_pagination

from ..utils.jwt_utils import has_permission, get_user_from_jwt

from django.contrib import messages
from django.db import IntegrityError
from datetime import datetime
from ..schema.company_drives import CompanyDrive  # Import the CompanyDrive model


def parse_json_data(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def apply_filters(queryset, filters):
    search = filters.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(enrollment__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(student_id__email__icontains=search)
        )
    if course := filters.get("course"):
        queryset = queryset.filter(course=course)
    if batch := filters.get("batch"):
        queryset = queryset.filter(joining_year=batch)
    if placement_status := filters.get("placement_status"):
        queryset = queryset.filter(placement_status=placement_status)
    if graduation_status := filters.get("graduation_status"):
        queryset = queryset.filter(graduation_status=graduation_status)

    return queryset


def format_student_data(paginated_students, page, perpage):
    return [
        {
            "sr_no": (page - 1) * perpage + i + 1,
            "id": s.student_id.id,
            "enrollment": s.enrollment,
            "name": f"{s.first_name} {s.last_name}",
            "email": safe_value(s.student_id, "email"),
            "course": safe_value(s.course, "name"),
            "batch": s.joining_year,
            "cgpa": s.cgpa,
            "placement_status": PlacementStatus(s.placement_status).label if s.placement_status is not None else None,
            "graduation_status": s.get_graduation_status_display(),
            "company_placedIn": safe_value(s.company_placedIn, "name"),
            "package": str(s.package) if s.package else None
        }
        for i, s in enumerate(paginated_students)
    ]

@permission_required('add_students')
@csrf_exempt
def student_registrations(request):
    return render(request, "student_registrations.html", {
        "page_title": "Student Registrations",
        "page_subtitle": "Add Student Details"
    })

@permission_required('add_students')
@csrf_exempt
def student_manual_registrations(request):
    if request.method == "POST":
        try:
            # Sanitize input data
            data = {key: value.strip() for key, value in request.POST.items()}

            # Validate required fields
            required_fields = ['email', 'phone', 'enrollment', 'first_name', 'last_name', 'joining_year']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return redirect("student_manual_registrations")

            # Check if email, phone, or enrollment already exists
            email = data.get('email')
            phone = data.get('phone')

            # Ensure enrollment is an integer
            try:
                enrollment = int(data.get('enrollment').strip())
            except ValueError:
                messages.error(request, "Enrollment must be a valid integer.")
                return redirect("student_manual_registrations")

            # Debugging: Log the enrollment value
            print(f"Checking enrollment: {enrollment}")

            # Query the database for existing enrollment
            existing_student = Student.objects.filter(enrollment=enrollment).first()
            if existing_student:
                # Debugging: Log the existing student details
                print(f"Existing student found: {existing_student}")
                messages.error(request, f"Student with enrollment number '{enrollment}' already exists.")
                return redirect("student_manual_registrations")

            if User.objects.filter(email=email).exists():
                messages.error(request, f"User with email '{email}' already exists.")
                return redirect("student_manual_registrations")

            if User.objects.filter(phone=phone).exists():
                messages.error(request, f"User with phone number '{phone}' already exists.")
                return redirect("student_manual_registrations")

            # Create user with hashed password
            password = data.get('password') or "placemate@123"
            hashed_password = make_password(password)
            user = User.objects.create(
                email=email,
                password=hashed_password,
                phone=phone
            )

            if Student.objects.filter(student_id=user).exists():
                messages.error(request, "A student record already exists for this user.")
                return redirect("student_manual_registrations")

            # Assign role to user
            student_role = Role.objects.filter(name="Student").first()
            if not student_role:
                messages.error(request, "Student role not found in the database.")
                return redirect("student_manual_registrations")

            UserRole.objects.create(user=user, role=student_role)

            # Fetch optional foreign keys
            course = Course.objects.filter(id=data.get('course')).first()
            if not course and data.get('course'):
                messages.error(request, "Invalid course selected.")
                return redirect("student_manual_registrations")

            city = City.objects.filter(id=data.get('city')).first()
            if not city and data.get('city'):
                messages.error(request, "Invalid city selected.")
                return redirect("student_manual_registrations")

            company = None
            if data.get('company_placed_in'):
                company = Company.objects.filter(name=data.get('company_placed_in')).first()
                if not company:
                    messages.error(request, "Invalid company selected.")
                    return redirect("student_manual_registrations")

            # Create student profile
            student = Student.objects.create(
                student_id=user,
                enrollment=enrollment,
                first_name=data.get('first_name'),
                middle_name=data.get('middle_name') or None,
                last_name=data.get('last_name'),
                dob=data.get('dob') or None,
                gender=data.get('gender') or None,
                joining_year=int(data.get('joining_year')),
                cgpa=float(data.get('cgpa')) if data.get('cgpa') else None,
                placement_status=int(data.get('placement_status', 0)),
                graduation_status=data.get('graduation_status', 'Pursuing'),
                course=course,
                city=city,
                address=data.get('address') or "",
                company_placedIn=company,
                package=float(data.get('package')) if data.get('package') else None
            )

            # Success message
            messages.success(request, f"Student {student.first_name} {student.last_name} added successfully.")
            return redirect("student_manual_registrations")

        except IntegrityError as e:
            # Debugging: Log the IntegrityError
            print(f"IntegrityError: {e}")
            messages.error(request, "Enrollment already exists.")
        except ValueError as ve:
            messages.error(request, f"Invalid data: {str(ve)}")
        except Exception as e:
            # Debugging: Log the unexpected error
            print(f"Unexpected error: {e}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    # GET request
    return render(request, "student_manual_registrations.html", {
        "page_title": "Student Manual Registrations",
        "page_subtitle": "Add Student Details",
        "courses": Course.objects.all(),
        "cities": City.objects.all(),
        "gender_choices": Gender.choices,
        "placement_status_choices": PlacementStatus.choices,
        "graduation_status_choices": GraduationStatus.choices
    })

@permission_required('view_students')
@csrf_exempt
def list_students(request):
    if request.method == "POST":
        data = parse_json_data(request)
        if data is None:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

        filters = data.get("filters", {})
        pagination = validate_pagination(data)
        if pagination is None:
            return JsonResponse({"message": "Page and perpage must be valid positive integers."}, status=400)

        page, perpage = pagination
        students = Student.objects.select_related("company_placedIn", "student_id", "course")
        students = apply_filters(students, filters).order_by("enrollment")

        paginated_students, total, pagination_data = paginate(students, page, perpage)
        result = format_student_data(paginated_students, page, perpage)

        # Check if the user has the 'add_students' and 'delete_students' permissions
        user_payload = get_user_from_jwt(request)
        user_role = user_payload.get("role") if user_payload else None
        can_add_student = has_permission(user_role, 'add_students')
        can_delete_student = has_permission(user_role, 'delete_students')

        return JsonResponse({
            "data": result,
            "total": total,
            "pagination": pagination_data,
            "permissions": {
                "can_add_students": can_add_student,
                "can_delete_students": can_delete_student
            }
        }, status=200)

    # Handle GET request
    try:
        page = int(request.GET.get("page", 1))
        perpage = int(request.GET.get("perpage", 10))
    except ValueError:
        page, perpage = 1, 10

    students = Student.objects.select_related("company_placedIn", "student_id", "course").order_by("enrollment")
    students = apply_filters(students, request.GET)

    paginated_students, total, pagination_data = paginate(students, page, perpage)
    start_index = (page - 1) * perpage

    # Filter dropdown options
    batches = Student.objects.values_list("joining_year", flat=True).distinct().order_by("joining_year")
    course_ids = Student.objects.values_list("course", flat=True).distinct()
    courses = Course.objects.filter(id__in=course_ids, is_active=True).order_by("name")
    course_options = [{"value": c.id, "label": c.name} for c in courses]

    placement_status_options = [{"value": val, "label": label} for val, label in PlacementStatus.choices]
    graduation_status_options = [{"value": val, "label": label} for val, label in GraduationStatus.choices]

    # Check if the user has the 'add_students' and 'delete_students' permissions
    user_payload = get_user_from_jwt(request)
    user_role = user_payload.get("role") if user_payload else None
    can_add_student = has_permission(user_role, 'add_students')
    can_delete_student = has_permission(user_role, 'delete_students')

    return render(request, "list_students.html", {
        "students": paginated_students,
        "pagination": pagination_data,
        "total": total,
        "start_index": start_index,
        "filter_options": {
            "batches": list(batches),
            "courses": course_options,
            "placement_statuses": placement_status_options,
            "graduation_statuses": graduation_status_options
        },
        "can_add_student": can_add_student,
        "can_delete_student": can_delete_student
    })

@permission_required('delete_students')
@csrf_exempt
def delete_student(request):
    if request.method != "POST":
        messages.error(request, "Only POST requests are allowed.")
        return redirect("list_students")

    student_id = request.POST.get("student_id")
    if not student_id:
        messages.error(request, "The 'student_id' field is required.")
        return redirect("list_students")

    try:
        # Attempt to retrieve the student
        student = Student.objects.get(student_id=student_id)
        student_name = f"{student.first_name} {student.last_name}"  # For better logging
        student.delete()

        # Add success message and redirect
        messages.success(request, f"The student '{student_name}' has been successfully removed from the system.")
        return redirect("list_students")

    except Student.DoesNotExist:
        # Handle case where student does not exist
        messages.error(request, f"The student with the provided ID does not exist.")
        return redirect("list_students")

    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An unexpected error occurred. Please try again later.")
        return redirect("list_students")

@permission_required('view_students')
@csrf_exempt
def view_student(request, student_id):
    try:
        # Retrieve the student by ID
        student = Student.objects.select_related("student_id", "course", "company_placedIn").get(student_id=student_id)

        # Fetch the list of courses
        courses = Course.objects.filter(is_active=True).order_by("name").values("id", "name")

        # Prepare the student details for rendering
        student_details = {
            "id": student.student_id.id,
            "name": f"{student.first_name} {student.last_name}",
            "email": student.student_id.email,
            "phone": student.student_id.phone,
            "enrollment": student.enrollment,
            "course": student.course.name if student.course else "N/A",
            "batch": f"{student.joining_year} - {student.joining_year + 4}" if student.joining_year else "N/A",
            "joining_year": student.joining_year or "N/A",  # Ensure joining_year is handled properly
            "cgpa": student.cgpa or "N/A",
            "placement_status": PlacementStatus(student.placement_status).label if student.placement_status is not None else "N/A",
            "graduation_status": student.get_graduation_status_display(),
            "company_placedIn": student.company_placedIn.name if student.company_placedIn else "N/A",
            "package": f"{student.package} LPA" if student.package else "N/A",
            "address": student.address or "N/A",
            "profile": student.profile or "N/A",
            "dob": student.dob.strftime('%Y-%m-%d') if student.dob else "N/A",
            "gender": student.gender if student.gender else "",  
        }

        # Render the student details page
        return render(request, "view_student.html", {
            "student": student_details,
            "page_title": "View Student",
            "page_subtitle": f"Details of {student.first_name} {student.last_name}",
            "courses": courses,  # Pass courses to the template
        })

    except Student.DoesNotExist:
        # Handle case where student does not exist
        messages.error(request, "The requested student does not exist.")
        return redirect("list_students")

    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect("list_students")

@permission_required('edit_students')
@csrf_exempt
def edit_student(request, student_id):
    try:
        # Retrieve the student by ID
        student = Student.objects.select_related("student_id", "course", "company_placedIn").get(student_id=student_id)

        if request.method == "POST":
            # Sanitize input data
            data = {key: value.strip() for key, value in request.POST.items()}

            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'graduation_status', 'placement_status', 'dob', 'enrollment']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return redirect("view_student", student_id=student_id)

            # Update student details
            student.enrollment = int(data.get('enrollment')) if data.get('enrollment') else student.enrollment
            student.first_name, _, student.last_name = data.get('name').partition(' ')
            student.student_id.email = data.get('email')
            student.student_id.phone = data.get('phone')
            student.address = data.get('address') or ""
            student.city = City.objects.filter(id=data.get('city')).first() if data.get('city') else None
            student.dob = data.get('dob') or None  # Ensure dob is updated
            student.gender = data.get('gender') or None  # Ensure gender is updated
            student.cgpa = float(data.get('cgpa')) if data.get('cgpa') else None
            student.graduation_status = data.get('graduation_status')

            # Map placement_status string to integer
            placement_status_map = {
                "not_placed": PlacementStatus.NOT_PLACED,
                "placed": PlacementStatus.PLACED,
                "internship": PlacementStatus.INTERN,
                "job_offer": PlacementStatus.JOB_OFFER,
            }
            student.placement_status = placement_status_map.get(data.get('placement_status').lower(), PlacementStatus.NOT_PLACED)

            student.company_placedIn = Company.objects.filter(name=data.get('company_placed_in')).first() if data.get('company_placed_in') else None
            student.package = float(data.get('package')) if data.get('package') else None
            student.course = Course.objects.filter(id=data.get('course')).first() if data.get('course') else None
            student.student_id.save()  # Save changes to the User model
            student.save()  # Save changes to the Student model

            # Success message
            messages.success(request, f"Student {student.first_name} {student.last_name} updated successfully.")
            return redirect("view_student", student_id=student_id)

        # GET request: Render the edit form
        return render(request, "view_student.html", {
            "student": student,
            "page_title": "Edit Student",
            "page_subtitle": f"Edit details of {student.first_name} {student.last_name}",
            "courses": Course.objects.all(),
            "cities": City.objects.all(),
            "placement_status_choices": PlacementStatus.choices,
            "graduation_status_choices": GraduationStatus.choices
        })

    except Student.DoesNotExist:
        # Handle case where student does not exist
        messages.error(request, "The requested student does not exist.")
        return redirect("list_students")

    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect("list_students")


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

        # Retrieve only active drives (status: SCHEDULED or ONGOING)
        active_drives = CompanyDrive.objects.filter(
            status__in=["scheduled", "ongoing"],  # Filter by active statuses
            start_date__lte=current_date,  # Ensure the drive has started
            end_date__gte=current_date  # Ensure the drive has not ended
        ).select_related('company')  # Optimize queries by selecting related company data

        # Format the drives for the template
        drives_data = [
            {
                "id": drive.id,
                "drive_name": drive.drive_name,
                "company_name": drive.company.name,
                "job_type": drive.job_type,
                "job_mode": drive.job_mode,
                "ug_package_min": drive.ug_package_min,
                "ug_package_max": drive.ug_package_max,
                "pg_package_min": drive.pg_package_min,
                "pg_package_max": drive.pg_package_max,
                "start_date": drive.start_date.strftime('%Y-%m-%d'),
                "end_date": drive.end_date.strftime('%Y-%m-%d'),
                "status": drive.status,
            }
            for drive in active_drives
        ]

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