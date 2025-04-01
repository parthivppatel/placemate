import jwt
import datetime
from django.conf import settings
from .schema.permissions import Permission
from .schema.role_permissions import RolePermission
from .schema.roles import Role
import random
import string

def generate_jwt_token(user, role):

    utc_now = datetime.datetime.now(datetime.timezone.utc)

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": role,
        "exp": utc_now + settings.JWT_EXPIRATION_DELTA,
        "iat": utc_now,
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

def has_permission(role_name, permission_name):
    permission = Permission.objects.filter(name=permission_name).first()
    role = Role.objects.filter(name =role_name).first()
    if not permission:
        return False

    return RolePermission.objects.filter(role=role, permission=permission).exists()


# Token generation for forgot password
def generate_otp_token(email, otp):
    payload = {
        "email": email,
        "otp": otp,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=60),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# Token Generation for Reset-Password
def generate_reset_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),  
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def generate_random_password():
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Randomly select characters and combine them into a password
    password = ''.join(random.choice(characters) for _ in range(12))
    
    return password