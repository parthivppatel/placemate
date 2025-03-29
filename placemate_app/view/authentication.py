from django.shortcuts import render,redirect
from ..schema import User
from django.db.models import Q


def home(request):
    return redirect('login')

def login(request):
    if(request.method == "POST"):
        email = request.POST['email']
        passwd = request.POST['passwd']

        if not email or not passwd:
            return render(request,'login.html',{'msg':'Required email or password','status':400})

        user = User.objects.filter(Q(email=email))
        print(user)

        print("hello workl...................................")
    return render(request,'login.html')
