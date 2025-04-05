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

def paginate(queryset, page, perpage):
    total = queryset.count()
    start = (page - 1) * perpage
    end = start + perpage
    paginated_data = queryset[start:end]

    pagination = {
        "page": page,
        "perpage": perpage,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None
    }

    return paginated_data, total, pagination

def ResponseModel(data=None, message="Success", status=200, pagination=None,total=0):
    return JsonResponse({
        "message": message,
        "status": status,
        "total":total,
        "pagination": pagination or {},
        "data": data or []
    }, status=status)