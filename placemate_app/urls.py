from django.urls import path

from .view.login import login
from .view.forgot_password import forgot_password
from .view.verify_otp import verify_otp, resend_otp

from .view.dashboard import dashboard
from .view.logout import logout
from .view.reset_password import reset_password
from .view.companies import register_company
urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),

    path('forgot-password/', forgot_password, name="forgot-password"),
    path('verify_otp/', verify_otp, name="verify-otp"),
    path('resend-otp/', resend_otp, name='resend-otp'),
    path('reset_password/', reset_password, name="reset-password"),
    path('resend_otp/', resend_otp, name="resend_otp"),
    path('logout/', logout, name="logout"),
    path('register_company/',register_company,name="register_company")
]