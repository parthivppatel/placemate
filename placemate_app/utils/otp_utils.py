import random
import datetime
import jwt

from django.conf import settings

# OTP Configurations from settings.py
JWT_SECRET = settings.JWT_SECRET 
JWT_ALGORITHM = settings.JWT_ALGORITHM

def generate_otp():
    """
    Generates a 6-digit random OTP.

    :return: 6-digit OTP as a string
    """
    return str(random.randint(100000, 999999))

def generate_otp_token(email, otp):
    payload = {
        "email": email,
        "otp": otp,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=settings.OTP_EXPIRATION_DELTA),  
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_otp_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("OTP has expired. Request a new OTP.")  
    except jwt.InvalidTokenError:
        raise ValueError("Invalid OTP token.")
