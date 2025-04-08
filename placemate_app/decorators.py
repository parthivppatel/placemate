from functools import wraps
from django.shortcuts import redirect,render
from django.contrib import messages
from .utils import decode_jwt_token, has_permission

 
def permission_required(*permission_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            token = request.COOKIES.get("jwt_token") 
            if not token:
                return redirect("login")

            payload = decode_jwt_token(token)
            if not payload:
                messages.error(request, "Invalid or expired token. Please log in again.")
                return redirect("login")

            user_role = payload["role"]
            if not any(has_permission(user_role, permission_name) for permission_name in permission_names): 
                return render(request,"403.html")

            request.user_data = payload
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
