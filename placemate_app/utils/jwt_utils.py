import jwt
import datetime

from django.conf import settings

from ..schema.permissions import Permission
from ..schema.role_permissions import RolePermission
from ..schema.roles import Role

# JWT Configurations from settings.py
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRY_HOURS = settings.JWT_EXPIRATION_DELTA // 3600  # Convert seconds to hours

RESET_TOKEN_EXPIRY_SECONDS = settings.RESET_TOKEN_EXPIRATION_DELTA

def generate_jwt_token(user, role):
    """
    Generates a JWT token containing user ID, email, and role.

    :param user: User object
    :param role: User role
    :return: Encoded JWT token as string
    """
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_reset_token(email):
    """
    Generates a reset token JWT for password reset.

    :param email: User's email
    :return: Encoded reset token as string
    """
    payload = {
        "email": email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=RESET_TOKEN_EXPIRY_SECONDS),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token):
    """
    Decodes and verifies a JWT token.

    :param token: JWT token string
    :return: Decoded payload if valid, else None
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None  
    except jwt.InvalidTokenError:
        return None  

def get_user_from_jwt(request):
    """
    Extracts user information from JWT token stored in request cookies.

    :param request: Django request object
    :return: Decoded user payload if valid, else None
    """
    token = request.COOKIES.get("jwt_token")
    return decode_jwt_token(token) if token else None

def has_permission(role_name, permission_name):
    permission = Permission.objects.filter(name=permission_name).first()
    role = Role.objects.filter(name =role_name).first()
    if not permission:
        return False

    return RolePermission.objects.filter(role=role, permission=permission).exists()