from django.http import JsonResponse

def safe_value(instance, attr, default=None):
    """Safely get attribute value if instance exists, else return default."""
    return getattr(instance, attr) if instance else default

def safe_deep_get(obj, attrs, default=None):
    for attr in attrs.split('.'):
        if obj is None:
            return default
        obj = getattr(obj, attr, None)
    return obj

def validate_pagination(data):
    try:
        page = int(data.get("page", 1))
        perpage = int(data.get("perpage", 10))
        if page < 1 or perpage < 1:
            raise ValueError
        return page, perpage
    except ValueError:
        return None

def paginate(queryset, page, perpage):
    total = queryset.count()
    start = (page - 1) * perpage
    end = start + perpage
    paginated_data = queryset[start:end]

    pagination = {
        "page": page,
        "perpage": perpage,
        "start_index":start,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None
    }

    return paginated_data, total, pagination

def ResponseModel(data=None, message="Success", status=200):
    return JsonResponse({
        "data": data,
        "status": status,
        "message": message,
    },status=status)


def update_mapper_by_id(model, main_field_id, related_field_id,main_id, incoming_ids):
    """
    Update a mapper table (like DriveSkill, JobCourse) using only IDs.

    Args:
        model (models.Model): The mapper model (e.g., DriveSkill).
        main_field_name (str): Name of the main object ForeignKey field (e.g., 'job').
        related_field_name (str): Name of the related object ForeignKey field (e.g., 'skill').
        main_id (int): ID of the main object.(job.id)
        related_ids (list): List of related object IDs from the frontend.
    """
    incoming_ids = set(incoming_ids or [])

    filter_kwargs = {f"{main_field_id}": main_id}

    existing_related_ids = set(
        model.objects.filter(**filter_kwargs).values_list(f"{related_field_id}", flat=True)
    )

    # New to add
    to_add = incoming_ids - existing_related_ids
    # Old to delete
    to_remove = existing_related_ids - incoming_ids

    if to_add:
        model.objects.bulk_create([
            model(**{
                f"{main_field_id}": main_id,
                f"{related_field_id}": rid
            }) for rid in to_add
        ])

    if to_remove:
        model.objects.filter(**filter_kwargs, **{f"{related_field_id}__in": to_remove}).delete()

def get_batch_year(student):
    """
    Returns the batch year for the student in the format 'YYYY-YYYY'.
    
    Args:
        student (Student): The Student instance to get the batch year for.
    
    Returns:
        str: The batch year in the format 'YYYY-YYYY' or None if course data is missing.
    """
    if student.course:
        graduation_year = student.joining_year + student.course.years
        return f"{student.joining_year}-{graduation_year}"
    return None