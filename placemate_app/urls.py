from django.urls import path

from .view.login import login
from .view.forgot_password import forgot_password
from .view.verify_otp import verify_otp, resend_otp

from .view.dashboard import dashboard
from .view.logout import logout
from .view.reset_password import reset_password
from .view.companies import register_company,view_company,list_companies,edit_company,delete_company,get_industries
from .view.countries_states_cities import get_countries,get_states,get_cities
# from .view.jobs import list_jobs,job_dropdowns,view_job,post_job,edit_job,delete_job
from .view.companydrives import list_drives,add_drive,edit_drive,delete_drive,view_drive,drive_dropdowns

from .view.students import student_registrations, student_manual_registrations, list_students, delete_student

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
    # path('company-dropdowns/',company_dropdowns,name="company_dropdowns"),

    # path('post-job/',post_job,name="post_job"),
    # path('edit-job/<int:id>/',edit_job,name="edit_job"),
    # path('list-jobs/',list_jobs,name="list_jobs"),
    # path('job-dropdowns/',job_dropdowns,name="job_dropdowns"),
    # path('view-job/<int:id>/',view_job,name="view_job"),
    # path('delete-job/<int:id>/',delete_job,name="delete_job"),

    path('list-drives/',list_drives,name="list_drives"),
    path('add-drive/',add_drive,name="add_drive"),
    path('edit-drive/<int:id>/',edit_drive,name="edit_drive"),
    path('delete-drive/<int:id>/',delete_drive,name="delete_drive"),
    path('view-drive/<int:id>/',view_drive,name="view_drive"),
    path('drive-dropdowns/',drive_dropdowns,name="drive_dropdowns"),

    path('get-countries/',get_countries,name="get_countries"),
    path('get-states/<int:country_id>/',get_states,name="get_states"),
    path('get-cities/<int:state_id>/',get_cities,name="get_cities"),

    # Manage Students
    path('students/manual_registrations/', student_manual_registrations, name='student_manual_registrations'),
    path('students/registrations/', student_registrations, name='student_registrations'),
    path('students/list/', list_students, name='list_students'),
    path('students/delete/', delete_student, name='delete_student'),


]