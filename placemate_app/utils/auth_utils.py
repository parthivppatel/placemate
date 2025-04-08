import jwt
import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from ..schema.users import User
from ..schema.user_roles import UserRole

from .jwt_utils import generate_jwt_token 

def authenticate_user(email, password):
    """Validates user credentials and returns user & role if valid."""
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None, "User does not exist."

    if not check_password(password, user.password):
        return None, "Invalid email or password."

    user_role = UserRole.objects.filter(user=user).select_related("role").first()
    role_name = user_role.role.name if user_role else "Unknown"

    return user, role_name

def set_jwt_cookie(response, user, role_name):
    """Generates JWT token and sets it as a secure HttpOnly cookie."""
    token = generate_jwt_token(user, role_name)
    response.set_cookie("jwt_token", token, httponly=True, secure=False)
    return response

def reset_user_password(user_email, new_password):
    """Resets a user's password after validating the token."""
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return None, "User not found."

    # Validate password strength
    if len(new_password) < 8:
        return None, "Password must be at least 8 characters long."

    # Hash the new password
    user.password = make_password(new_password)
    user.save()

    return user, "Password reset successfully."

def validate_reset_token(reset_token):
    """Validates the reset token and returns the payload if valid."""
    try:
        payload = jwt.decode(reset_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        # Check if the token is expired
        if datetime.datetime.now(datetime.timezone.utc) > datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc):
            return None, "Reset session expired. Request a new password reset link."
        
        return payload, None  # Token is valid
    except jwt.ExpiredSignatureError:
        return None, "Reset session expired. Request a new password reset link."
    except jwt.InvalidTokenError:
        return None, "Invalid reset session."
