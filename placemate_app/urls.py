from django.urls import path

from .view.login import login
from .view.forgot_password import forgot_password
from .view.verify_otp import verify_otp, resend_otp

from .view.dashboard import dashboard
from .view.logout import logout
from .view.reset_password import reset_password
from .view.companies import register_company,view_company,company_dropdowns,list_companies,edit_company,delete_company,get_industries
from .view.countries_states_cities import get_countries,get_states,get_cities
from .view.jobs import list_jobs

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),

    path('forgot-password/', forgot_password, name="forgot-password"),
    path('verify_otp/', verify_otp, name="verify-otp"),
    path('resend-otp/', resend_otp, name='resend-otp'),
    path('reset_password/', reset_password, name="reset-password"),
    path('resend_otp/', resend_otp, name="resend_otp"),
    
    path('get-industries/',get_industries,name="get_industries"),

    path('register_company/',register_company,name="register_company"),
    path('view-company/<int:id>/',view_company,name="view_company"),
    path('list-companies/',list_companies,name="list_companies"),
    path('edit-company/<int:id>/',edit_company,name="edit_company"),
    path('delete-company/<int:id>/',delete_company,name="delete_company"),
    path('company-dropdowns/',company_dropdowns,name="company_dropdowns"),

    path('list-jobs/',list_jobs,name="list_jobs"),

    path('get-countries/',get_countries,name="get_countries"),
    path('get-states/<int:country_id>/',get_states,name="get_states"),
    path('get-cities/<int:state_id>/',get_cities,name="get_cities")
]