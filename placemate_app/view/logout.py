from django.shortcuts import redirect

def logout(request):
    respone = redirect("login")
    respone.delete_cookie("jwt_token")
    return respone
