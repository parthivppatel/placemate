from django.shortcuts import redirect
from django.contrib import messages

def logout(request):
    response = redirect("login")

    response.delete_cookie("jwt_token")
    
    response.delete_cookie("otp_token")
    
    response.delete_cookie("reset_token")
    
    # Clear any existing messages from the session
    messages.get_messages(request).used = True

    return response