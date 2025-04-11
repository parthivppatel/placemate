import json

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from ..decorators import permission_required
from ..schema.students import Student, PlacementStatus, GraduationStatus
from ..schema.course import Course
from ..utils.helper_utils import paginate, safe_value


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

def student_manual_registrations(request):
    return render(request, "student_manual_registrations.html", {
        "page_title": "Student Manual Registrations",
        "page_subtitle": "Add Student Details"
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