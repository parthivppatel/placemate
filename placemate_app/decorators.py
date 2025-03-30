from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .utils import decode_jwt_token, has_permission

 
def permission_required(permission_name):
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
            if not has_permission(user_role, permission_name):
                messages.error(request, "You do not have permission to access this page.")

            request.user_data = payload
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
