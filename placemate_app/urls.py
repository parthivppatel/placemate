from django.urls import path

from .view.login import login
from .view.dashboard import dashboard
from .view.logout import logout
from .view.forgot_password import forgot_password, verify_otp, reset_password, resend_otp
from .view.companies import register_company

urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('login/', login, name="login"),
    path('forgot-password/', forgot_password, name="forgot-password"),
    path('verify_otp/', verify_otp, name="verify-otp"),
    path('reset_password/', reset_password, name="reset-password"),
    path('resend_otp/', resend_otp, name="resend_otp"),
    path('logout/', logout, name="logout"),
    path('register_company/',register_company,name="register_company")
]