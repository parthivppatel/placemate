from placemate_app.view import authentication
from django.urls import path

urlpatterns = [
    path('', authentication.home,name="home"),
    path('login/',authentication.login,name="login")
]