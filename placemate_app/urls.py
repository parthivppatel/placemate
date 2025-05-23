from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .view.login import login, roleloggin
from .view.forgot_password import forgot_password
from .view.verify_otp import verify_otp, resend_otp

from .view.dashboard import dashboard
from .view.logout import logout
from .view.reset_password import reset_password
from .view.companies import register_company,view_company,list_companies,edit_company,delete_company,company_registration_page,edit_company_page,shortlisted_students,placement_action
from .view.countries_states_cities import get_countries,get_states,get_cities,get_city_with_name
# from .view.jobs import list_jobs,job_dropdowns,view_job,post_job,edit_job,delete_job
from .view.companydrives import list_drives,add_drive,edit_drive,edit_drive_page,delete_drive,view_drive,add_drive_page,drive_applicants,application_action

from .view.students import student_registrations, student_manual_registrations, view_student, edit_student, delete_student, list_students
from .view.student import student_profile, student_edit_student, list_student_drives, student_drive_details, student_drive_applications
from .view.members import list_members,delete_member,view_member,member_registration_page,add_member,edit_member_page,edit_member

from .view.CompanyService.company import company_profile

from placemate_app.utils.reset_password_utils import profile_reset_password

urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('login/', login, name="login"),
    path('roleloggin/', roleloggin, name="roleloggin"),
    path('logout/', logout, name="logout"),

    path('profile-reset-password/', profile_reset_password, name="profile_reset_password"),

    path('forgot-password/', forgot_password, name="forgot-password"),
    path('verify_otp/', verify_otp, name="verify-otp"),
    path('resend-otp/', resend_otp, name='resend-otp'),
    path('reset_password/', reset_password, name="reset-password"),
    path('resend_otp/', resend_otp, name="resend_otp"),
    
    # path('get-industries/',get_industries,name="get_industries"),
    path('members/list-members/',list_members,name="list_members"),
    path('members/delete-member/',delete_member,name="delete_member"),
    path('members/view-member/<int:id>',view_member,name="view_member"),
    path('members/register-member/',member_registration_page,name="member_registration_page"),
    path('members/register/',add_member,name="add_member"),
    path('members/edit/<int:id>',edit_member_page,name="edit_member_page"),
    path('members/edit-member/<int:id>',edit_member,name="edit_member"),


    path('companies/register_company/',register_company,name="register_company"),
    path('companies/register/',company_registration_page,name="company_registration_page"),
    path('companies/edit/<int:id>',edit_company_page,name="edit_company_page"),
    path('companies/view-company/<int:id>/',view_company,name="view_company"),
    path('companies/list-companies/',list_companies,name="list_companies"),
    path('companies/edit-company/<int:id>/',edit_company,name="edit_company"),
    path('companies/delete-company/',delete_company,name="delete_company"),
    path('companies/shortlisted-students/',shortlisted_students,name="shortlisted_students"),
    path('companies/placement-action/',placement_action,name="placement_action"),
    # path('company-dropdowns/',company_dropdowns,name="company_dropdowns"),

    # path('post-job/',post_job,name="post_job"),
    # path('edit-job/<int:id>/',edit_job,name="edit_job"),
    # path('list-jobs/',list_jobs,name="list_jobs"),
    # path('job-dropdowns/',job_dropdowns,name="job_dropdowns"),
    # path('view-job/<int:id>/',view_job,name="view_job"),
    # path('delete-job/<int:id>/',delete_job,name="delete_job"),

    path('drives/list-drives/',list_drives,name="list_drives"),
    path('drives/add-drive/',add_drive,name="add_drive"),
    path('drives/add-drive-page/',add_drive_page,name="add_drive_page"),
    path('drives/edit-drive-page/<int:id>',edit_drive_page,name="edit_drive_page"),
    path('drives/edit-drive/<int:id>/',edit_drive,name="edit_drive"),
    path('drives/delete-drive/',delete_drive,name="delete_drive"),
    path('drives/view-drive/<int:id>/',view_drive,name="view_drive"), 
    path('drives/drive-applicants/<int:id>/',drive_applicants,name="drive_applicants"), 
    path('drives/application-action/<int:id>/',application_action,name="application_action"), 
    

    path('get-countries/',get_countries,name="get_countries"),
    path('get-states/<int:country_id>/',get_states,name="get_states"),
    path('get-cities/<int:state_id>/',get_cities,name="get_cities"),
    path('get-cities-by-name/',get_city_with_name,name="get_city_with_name"),
    

    # Student Manage by Placement Cell
    path('students/manual_registrations/', student_manual_registrations, name='student_manual_registrations'),
    path('students/registrations/', student_registrations, name='student_registrations'),
    path('students/list/', list_students, name='list_students'),
    path('students/view/<int:student_id>/', view_student, name='view_student'),
    path('students/edit_student/<int:student_id>/', edit_student, name='edit_student'),
    path('students/delete/', delete_student, name='delete_student'),

    # Manage by Students
    path('student/drives/', list_student_drives, name='list_student_drives'),
    path('student/profile/<int:student_id>/', student_profile, name='student_profile'),
    path('student/edit/<int:student_id>/', student_edit_student, name='student_edit_student'),
    path('student/drive-details/<int:drive_id>/', student_drive_details, name='student_drive_details'),
    path('student/applications/<int:student_id>/', student_drive_applications, name='student_drives_application'),

    # Manage by Company
    path('company/profile/', company_profile, name='company_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)