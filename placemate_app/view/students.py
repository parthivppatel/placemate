import json
from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from ..decorators import permission_required
from ..schema.students import Student
from ..utils.helper_utils import ResponseModel, paginate, safe_value


@permission_required('view_students')
@csrf_exempt
def list_students(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseModel({}, "Invalid JSON data", 400)

        filters = data.get("filters", {})
        
        try:
            page = int(data.get("page", 1))
            perpage = int(data.get("perpage", 10))

            if page < 1 or perpage < 1:
                return ResponseModel({}, "Page and per page must be positive integers", 400)
        except ValueError:
            return ResponseModel({}, "Page and per page must be valid integers.", 400)

        students = Student.objects.select_related("company_placedIn", "student_id")

        # Filtering
        if search := filters.get("search", "").strip():
            students = students.filter(
                Q(enrollment__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(student_id__email__icontains=search)
            )

        if "course" in filters:
            students = students.filter(course__iexact=filters["course"])

        if "batch" in filters:
            students = students.filter(joining_year=filters["batch"])

        if "placement_status" in filters:
            students = students.filter(placement_status=filters["placement_status"])

        if "graduation_status" in filters:
            students = students.filter(graduation_status=filters["graduation_status"])

        # Default ordering
        students = students.order_by("enrollment")

        # Pagination
        students, total, pagination = paginate(students, page, perpage)

        result = [
            {
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
            for s in students
        ]

        response = {
            "data": result,
            "total": total,
            "pagination": pagination
        }

        return ResponseModel(response, "Success", 200)

    # GET request → render default template
    students = Student.objects.select_related("company_placedIn", "student_id").order_by("enrollment")
    students, total, pagination = paginate(students, 1, 10)

    context = {
        "students": students,
        "pagination": pagination,
        "total": total
    }

    return render(request, "list_students.html", context)
