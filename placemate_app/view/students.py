import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from ..decorators import permission_required
from ..schema.students import Student
from ..utils.helper_utils import paginate, safe_value

def parse_json_data(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


# Helper function to validate pagination
def validate_pagination(data):
    try:
        page = int(data.get("page", 1))
        perpage = int(data.get("perpage", 10))
        if page < 1 or perpage < 1:
            raise ValueError
        return page, perpage
    except ValueError:
        return None


# Helper function to apply filters to the queryset
def apply_filters(queryset, filters):
    if search := filters.get("search", "").strip():
        queryset = queryset.filter(
            Q(enrollment__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(student_id__email__icontains=search)
        )

    if course := filters.get("course"):
        queryset = queryset.filter(course__iexact=course)

    if batch := filters.get("batch"):
        queryset = queryset.filter(joining_year=batch)

    if placement_status := filters.get("placement_status"):
        queryset = queryset.filter(placement_status=placement_status)

    if graduation_status := filters.get("graduation_status"):
        queryset = queryset.filter(graduation_status=graduation_status)

    return queryset


# Helper function to format the student data for response
def format_student_data(paginated_students, page, perpage):
    return [
        {
            "sr_no": (page - 1) * perpage + i + 1,
            "id": s.id,
            "enrollment": s.enrollment,
            "name": f"{s.first_name} {s.last_name}",
            "email": safe_value(s.student_id, "email"),
            "course": s.course,
            "batch": s.joining_year,
            "cgpa": s.cgpa,
            "placement_status": s.placement_status,
            "graduation_status": s.graduation_status,
            "company_placedIn": safe_value(s.company_placedIn, "name"),
            "package": str(s.package) if s.package else None
        }
        for i, s in enumerate(paginated_students)
    ]


# List Students API View
@permission_required('view_students')
@csrf_exempt
def list_students(request):
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if request.method == "POST":
        # Parse JSON and validate pagination
        data = parse_json_data(request)
        if data is None:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

        filters = data.get("filters", {})
        pagination = validate_pagination(data)
        if pagination is None:
            return JsonResponse({"message": "Page and perpage must be valid positive integers."}, status=400)

        page, perpage = pagination

        # Base queryset with related fields
        students = Student.objects.select_related("company_placedIn", "student_id")

        # Apply filters to the queryset
        students = apply_filters(students, filters)

        # Sort and paginate
        students = students.order_by("enrollment")
        paginated_students, total, pagination = paginate(students, page, perpage)

        # Format response data
        result = format_student_data(paginated_students, page, perpage)

        return JsonResponse({
            "data": result,
            "total": total,
            "pagination": pagination
        }, status=200)

    # Initial GET load
    try:
        page = int(request.GET.get("page", 1))
        perpage = int(request.GET.get("perpage", 10))
    except ValueError:
        page, perpage = 1, 10

    # Base queryset for students
    students = Student.objects.select_related("company_placedIn", "student_id").order_by("enrollment")

    # Apply filters from query parameters
    filters = request.GET
    students = apply_filters(students, filters)

    # Paginate using helper
    paginated_students, total, pagination = paginate(students, page, perpage)
    start_index = (page - 1) * perpage

    # Fetch distinct filter options dynamically
    batches = Student.objects.values_list("joining_year", flat=True).distinct().order_by("joining_year")
    courses = Student.objects.values_list("course", flat=True).distinct().order_by("course")
    statuses = Student.objects.values_list("placement_status", flat=True).distinct().order_by("placement_status")

    # Pass dynamic filter options to the template
    return render(request, "list_students.html", {
        "students": paginated_students,
        "pagination": pagination,
        "total": total,
        "start_index": start_index,  # For Sr. No on initial render
        "filter_options": {
            "batches": list(batches),
            "courses": list(courses),
            "statuses": list(statuses)
        }
    })
