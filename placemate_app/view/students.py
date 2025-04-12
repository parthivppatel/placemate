import json
from django.contrib.auth.hashers import make_password, check_password

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from ..decorators import permission_required
from ..schema.users import User
from ..schema.students import Student, PlacementStatus, GraduationStatus
from ..schema.course import Course
from ..schema.roles import Role
from ..schema.user_roles import UserRole
from ..schema.cities import City
from ..utils.helper_utils import paginate, safe_value

from django.contrib import messages
from django.db import IntegrityError

def parse_json_data(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def validate_pagination(data):
    try:
        page = int(data.get("page", 1))
        perpage = int(data.get("perpage", 10))
        if page < 1 or perpage < 1:
            raise ValueError
        return page, perpage
    except ValueError:
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
            "id": s.id,
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

            # Debugging logs
            print("Received POST request for student registration")
            print(f"Sanitized Request data: {data}")

            # Validate required fields
            required_fields = ['email', 'phone', 'enrollment', 'first_name', 'last_name', 'joining_year']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
                print(f"Missing fields: {missing_fields}")
                return redirect("student_manual_registrations")

            # Check if email, phone, or enrollment already exists
            email = data.get('email')
            phone = data.get('phone')
            enrollment = data.get('enrollment')

            if User.objects.filter(email=email).exists():
                messages.error(request, f"User with email '{email}' already exists.")
                print(f"Email already exists: {email}")
                return redirect("student_manual_registrations")

            if User.objects.filter(phone=phone).exists():
                messages.error(request, f"User with phone number '{phone}' already exists.")
                print(f"Phone number already exists: {phone}")
                return redirect("student_manual_registrations")

            if Student.objects.filter(enrollment=enrollment).exists():
                messages.error(request, f"Student with enrollment number '{enrollment}' already exists.")
                print(f"Enrollment number already exists: {enrollment}")
                return redirect("student_manual_registrations")

            # Create user with hashed password
            password = data.get('password') or "placemate@123"
            hashed_password = make_password(password)
            user = User.objects.create(
                email=email,
                password=hashed_password,
                phone=phone
            )

            # Assign role to user
            student_role = Role.objects.filter(name="Student").first()
            if not student_role:
                messages.error(request, "Student role not found in the database.")
                print("Student role not found.")
                return redirect("student_manual_registrations")

            UserRole.objects.create(user=user, role=student_role)

            # Fetch optional foreign keys
            course = Course.objects.filter(id=data.get('course')).first()
            if not course and data.get('course'):
                messages.error(request, "Invalid course selected.")
                print(f"Invalid course ID: {data.get('course')}")
                return redirect("student_manual_registrations")

            city = City.objects.filter(id=data.get('city')).first()
            if not city and data.get('city'):
                messages.error(request, "Invalid city selected.")
                print(f"Invalid city ID: {data.get('city')}")
                return redirect("student_manual_registrations")

            # Create student profile
            student = Student.objects.create(
                student_id=user,
                enrollment=int(enrollment),
                first_name=data.get('first_name'),
                middle_name=data.get('middle_name') or None,
                last_name=data.get('last_name'),
                dob=data.get('dob') or None,
                gender=data.get('gender') or None,
                joining_year=int(data.get('joining_year')),
                cgpa=float(data.get('cgpa')) if data.get('cgpa') else None,
                profile=data.get('profile') or "",
                placement_status=int(data.get('placement_status', 0)),
                graduation_status=data.get('graduation_status', 'Pursuing'),
                course=course,
                city=city,
                address=data.get('address') or ""
            )

            # Success message
            messages.success(request, f"Student {student.first_name} {student.last_name} added successfully.")
            print(f"Student created successfully: {student}")
            return redirect("student_manual_registrations")

        except IntegrityError:
            messages.error(request, "Enrollment already exists.")
            print("IntegrityError: Enrollment already exists.")
        except ValueError as ve:
            messages.error(request, f"Invalid data: {str(ve)}")
            print(f"ValueError: {str(ve)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            print(f"Exception: {str(e)}")

    # GET request
    return render(request, "student_manual_registrations.html", {
        "page_title": "Student Manual Registrations",
        "page_subtitle": "Add Student Details",
        "courses": Course.objects.all(),
        "cities": City.objects.all()
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

        return JsonResponse({
            "data": result,
            "total": total,
            "pagination": pagination_data
        }, status=200)

    # GET request
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
        }
    })

@permission_required('delete_students')
@csrf_exempt
def delete_student(request):
    if request.method != "POST":
        return JsonResponse({"message": "Only POST requests are allowed."}, status=405)

    student_id = request.POST.get("student_id")
    if not student_id:
        return JsonResponse({"message": "student_id is required"}, status=400)

    try:
        student = Student.objects.get(id=student_id)
        student.delete()
        return JsonResponse({
            "message": f"Student {student_id} deleted successfully.",
            "deleted_count": 1
        }, status=200)
    except Student.DoesNotExist:
        return JsonResponse({"message": "Student does not exist."}, status=404)