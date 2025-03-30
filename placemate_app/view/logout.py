from django.shortcuts import redirect
from django.contrib import messages

def logout(request):
    respone = redirect("login")
    respone.delete_cookie("jwt_token")

    list(messages.get_messages(request))
    
    return respone
