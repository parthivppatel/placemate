from django.contrib import admin
from .schema.users import User
from .schema.roles import Role
from .schema.permissions import Permission
from .schema.role_permissions import RolePermission
from .schema.user_roles import UserRole
from .schema.countries import Country
from .schema.states import State
from .schema.cities import City
from .schema.branch import Branch
from .schema.course import Course
from .schema.placement_cell_members import PlacementCellMember
from .schema.authorities import Authority
from .schema.industry import Industry
from .schema.job_positions import JobPosition
from .schema.companies import Company
from .schema.students import Student
from .schema.skills import Skill
from .schema.drive_courses import DriveCourses
from .schema.drive_locations import DriveLocation
from .schema.drive_skills import DriveSkill
from .schema.drive_applications import DriveApplication
from .schema.interviews import Interview 
from .schema.placement_offers import PlacementOffer
from .schema.notifications import Notification
from .schema.company_drive_jobs import CompanyDriveJobs
from .schema.company_drives import CompanyDrive
# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserRole)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Branch)
admin.site.register(Course)
admin.site.register(PlacementCellMember)
admin.site.register(Authority)
admin.site.register(Industry)
admin.site.register(JobPosition)
admin.site.register(DriveApplication)
admin.site.register(DriveCourses)
admin.site.register(DriveLocation)
admin.site.register(Notification)
admin.site.register(Company)
admin.site.register(Student)
admin.site.register(Skill)
admin.site.register(DriveSkill)
admin.site.register(Interview) 
admin.site.register(PlacementOffer) 
admin.site.register(CompanyDriveJobs)
admin.site.register(CompanyDrive)