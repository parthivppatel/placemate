import json
from django.contrib.auth.hashers import make_password

from django.utils import timezone 

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from ..utils.email_utils import send_student_registration_email
from ..decorators import permission_required
from ..schema.users import User
from ..schema.students import Student, PlacementStatus, GraduationStatus, Gender, Company
from ..schema.course import Course
from ..schema.roles import Role
from ..schema.user_roles import UserRole
from ..schema.cities import City
from ..utils.helper_utils import paginate, safe_value,validate_pagination, ResponseModel,get_batch_year

from ..utils.jwt_utils import has_permission, get_user_from_jwt

from django.contrib import messages
from django.db import IntegrityError
from ..schema.company_drives import CompanyDrive  # Import the CompanyDrive model
from ..schema.drive_applications import DriveApplication


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
def student_registrations(request):
    return render(request, "student_registrations.html", {
        "page_title": "Student Registrations",
        "page_subtitle": "Add Student Details"
    })

@permission_required('add_students')
def student_manual_registrations(request):
    if request.method == "POST":
        try:
            data = {key: value.strip() for key, value in request.POST.items()}

            required_fields = ['email', 'phone', 'enrollment', 'first_name', 'last_name', 'joining_year']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return redirect("student_manual_registrations")

            email = data.get('email')
            phone = data.get('phone')

            try:
                enrollment = int(data.get('enrollment').strip())
            except ValueError:
                messages.error(request, "Enrollment must be a valid integer.")
                return redirect("student_manual_registrations")

            print(f"Checking enrollment: {enrollment}")

            existing_student = Student.objects.filter(enrollment=enrollment).first()
            if existing_student:
                print(f"Existing student found: {existing_student}")
                messages.error(request, f"Student with enrollment number '{enrollment}' already exists.")
                return redirect("student_manual_registrations")

            if User.objects.filter(email=email).exists():
                messages.error(request, f"User with email '{email}' already exists.")
                return redirect("student_manual_registrations")

            if User.objects.filter(phone=phone).exists():
                messages.error(request, f"User with phone number '{phone}' already exists.")
                return redirect("student_manual_registrations")

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

            student_role = Role.objects.filter(name="Student").first()
            if not student_role:
                messages.error(request, "Student role not found in the database.")
                return redirect("student_manual_registrations")

            UserRole.objects.create(user=user, role=student_role)

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

            try:
                full_name = f"{student.first_name} {student.last_name}"
                send_student_registration_email(
                    email=email,
                    password=password if data.get('password') else "placemate@123"
                )
                messages.success(request, f"Welcome email sent to {email}.")
            except Exception as e:
                print(f"Failed to send welcome email: {str(e)}")
                messages.warning(request, f"Student registered but failed to send welcome email: {str(e)}")

            messages.success(request, f"Student {student.first_name} {student.last_name} added successfully.")
            return redirect("student_manual_registrations")

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            messages.error(request, "Enrollment already exists.")
        except ValueError as ve:
            messages.error(request, f"Invalid data: {str(ve)}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, "student_manual_registrations.html", {
        "page_title": "Student Manual Registrations",
        "page_subtitle": "Add Student Details",
        "courses": Course.objects.all(),
        "cities": City.objects.all(),
        "gender_choices": Gender.choices,
        "placement_status_choices": PlacementStatus.choices,
        "graduation_status_choices": GraduationStatus.choices
    })

@permission_required('delete_students')
def delete_student(request):
    if request.method != "POST":
        messages.error(request, "Only POST requests are allowed.")
        return redirect("list_students")

    student_id = request.POST.get("student_id")
    if not student_id:
        messages.error(request, "The 'student_id' field is required.")
        return redirect("list_students")

    try:
        student = Student.objects.get(student_id=student_id)
        student_name = f"{student.first_name} {student.last_name}"  
        student.delete()

        messages.success(request, f"The student '{student_name}' has been successfully removed from the system.")
        return redirect("list_students")

    except Student.DoesNotExist:
        messages.error(request, f"The student with the provided ID does not exist.")
        return redirect("list_students")

    except Exception as e:
        messages.error(request, f"An unexpected error occurred. Please try again later.")
        return redirect("list_students")

@permission_required('view_students')
def view_student(request, student_id):
    try:
        student = Student.objects.select_related("student_id", "course", "company_placedIn").get(student_id=student_id)

        courses = Course.objects.filter(is_active=True).order_by("name").values("id", "name")

        student_details = {
            "id": student.student_id.id,
            "name": f"{student.first_name} {student.last_name}",
            "email": student.student_id.email,
            "phone": student.student_id.phone,
            "enrollment": student.enrollment,
            "course": student.course.name if student.course else "N/A",
            "batch": get_batch_year(student) if student.joining_year else "N/A",
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

        user_payload = get_user_from_jwt(request)
        user_role = user_payload.get("role") if user_payload else None
        can_view_applicants = has_permission(user_role, 'view_applicants')

        context = {
            "student": student_details,
            "page_title": "View Student",
            "page_subtitle": f"Details of {student.first_name} {student.last_name}",
            "courses": courses,  
            "permissions":{
                "view_applicants":can_view_applicants
            }
        }

        drive_id = request.GET.get("drive_id")
        if can_view_applicants and drive_id:
            resume_link = DriveApplication.objects.filter(drive_id = drive_id,student_id = student_id).values("resume_link").first()
            context.update({'resume':resume_link,'drive_id':drive_id})

        return render(request, "view_student.html",context)

    except Student.DoesNotExist:
        messages.error(request, "The requested student does not exist.")
        return redirect("list_students")

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect("list_students")

@permission_required('edit_students')
def edit_student(request, student_id):
    try:
        student = Student.objects.select_related("student_id", "course", "company_placedIn").get(student_id=student_id)

        if request.method == "POST":
            data = {key: value.strip() for key, value in request.POST.items()}

            required_fields = ['name', 'email', 'phone', 'graduation_status', 'placement_status', 'dob', 'enrollment']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                return redirect("view_student", student_id=student_id)

            student.enrollment = int(data.get('enrollment')) if data.get('enrollment') else student.enrollment
            student.first_name, _, student.last_name = data.get('name').partition(' ')
            student.student_id.email = data.get('email')
            student.student_id.phone = data.get('phone')
            student.address = data.get('address') or ""
            student.city = City.objects.filter(id=data.get('city')).first() if data.get('city') else None
            student.dob = data.get('dob') or None  
            student.gender = data.get('gender') or None  
            student.cgpa = float(data.get('cgpa')) if data.get('cgpa') else None
            student.graduation_status = data.get('graduation_status')

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
            student.student_id.save()  
            student.save()  

            messages.success(request, f"Student {student.first_name} {student.last_name} updated successfully.")
            return redirect("view_student", student_id=student_id)

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
        messages.error(request, "The requested student does not exist.")
        return redirect("list_students")

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect("list_students")

@permission_required('view_students')
def list_students(request):
    page, perpage = 1, 10

    if request.method == "GET":
        data = request.GET

        validate_pg = validate_pagination(data)
        if validate_pg is None:
            return ResponseModel({},"Page and perpage must be valid positive integers", 400)
        page, perpage = validate_pg

        students = Student.objects.select_related("company_placedIn", "student_id", "course")

        if search := data.get("search", "").strip():
            students = students.filter(
                Q(student_id__email__icontains=search) |
                Q(enrollment__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        if batch := data.get("joining_year", "").strip():
            students = students.filter(joining_year=batch)

        if course := data.get("course", "").strip():
            students = students.filter(course=course)

        if placement_status := data.get("placement_status", "").strip():
            students = students.filter(placement_status=placement_status)

        if graduation_status := data.get("graduation_status", "").strip():
            students = students.filter(graduation_status=graduation_status)

        sort = data.get("sort", {})
        sort_field = sort.get("field", "").strip()
        sort_type = sort.get("type", "asc").lower()

        ordering = "enrollment"
        if sort_field:
            if sort_field == "name":
                ordering = "first_name"
            elif sort_field == "email":
                ordering = "student_id__email"
            elif sort_field == "phone":
                ordering = "student_id__phone"
            elif sort_field == "cgpa":
                ordering = "cgpa"
            elif sort_field == "joining_year":
                ordering = "joining_year"

            if sort_type == "desc":
                ordering = f"-{ordering}"

        students = students.order_by(ordering)

        students, total, pagination = paginate(students, page, perpage)

        result = []
        for student in students:
            result.append({
                "id": student.student_id.id,
                "email": student.student_id.email,
                "name": f"{student.first_name} {student.last_name}",
                "enrollment": student.enrollment,
                "cgpa": student.cgpa,
                "phone": student.student_id.phone,
                "batch": get_batch_year(student) if student.joining_year else "N/A",  
                "course": safe_value(student.course, "name"),
                "placement_status": student.get_placement_status_display(),  
                "graduation_status": student.get_graduation_status_display(),
                "company_placedIn": safe_value(student.company_placedIn, "name")
            })

        batches = list(Student.objects.values_list("joining_year", flat=True).distinct().order_by("joining_year"))
        course_ids = Student.objects.values_list("course", flat=True).distinct()
        courses = Course.objects.filter(id__in=course_ids, is_active=True).order_by("name")
        course_options = [{"value": c.id, "label": c.name} for c in courses]

        placement_status_options = [{"value": val, "label": label} for val, label in PlacementStatus.choices]
        graduation_status_options = [{"value": val, "label": label} for val, label in GraduationStatus.choices]

        filter_options = {
            "batches": batches,
            "courses": course_options,
            "placement_statuses": placement_status_options,
            "graduation_statuses": graduation_status_options
        }

        user_payload = get_user_from_jwt(request)
        user_role = user_payload.get("role") if user_payload else None
        can_add_student = has_permission(user_role, 'add_students')
        can_delete_student = has_permission(user_role, 'delete_students')
        can_view_student = has_permission(user_role, 'view_students')

        return render(request, "list_students.html", {
            "students": result,
            "total": total,
            "pagination": pagination,
            "filter_options": filter_options,
            "permissions": {
                "can_add_student": can_add_student,
                "can_delete_student": can_delete_student,
                "can_view_student": can_view_student
            }
        })

    return redirect("dashboard")