import jwt
import datetime
from django.conf import settings

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