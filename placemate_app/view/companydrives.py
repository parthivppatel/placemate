from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from ..schema.companies import Company
from ..schema.students import Student
from ..schema.drive_skills import DriveSkill
from ..schema.drive_courses import DriveCourses
from ..schema.drive_locations import DriveLocation
from ..schema.company_drives import CompanyDrive,JobMode,JobType,DriveStatus
from ..schema.drive_applications import DriveApplication
from ..schema.skills import Skill
from ..schema.course import Course
from ..schema.cities import City
from ..schema.company_drive_jobs import CompanyDriveJobs
from ..schema.placement_offers import PlacementOffer 
from ..utils.random_password_utils import generate_random_password
from ..decorators import permission_required
from ..utils.email_utils import send_registration_email,send_drive_emails
from django.db.models import Q,Count, F, ExpressionWrapper, IntegerField
from ..utils.helper_utils import safe_value,safe_deep_get,paginate,ResponseModel,update_mapper_by_id
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction,IntegrityError
import json
import threading
import re
from datetime import datetime


@permission_required('view_drives')   
def list_drives(request):
    if request.method == "POST":
        data = json.loads(request.body)
        filters = data.get("filters", {})
        sort = data.get("sort", {})
        try:
            page = int(data.get("page", 1))
            perpage = int(data.get("perpage", 10))

            if page < 1 or perpage < 1:
                return ResponseModel({},"Page and per page must be positive integers",400)
        except:
            return ResponseModel({},"Page and per page must be valid integers.",400)


        # data gathering
        drives = CompanyDrive.objects.select_related("company").annotate(
            applicants=Count("driveapplication")
        )

        # filtering
        if search := filters.get("search","").strip():
            drives = drives.filter(Q(drive_name__icontains=search) | Q(company__name__icontains=search))

        if "status" in filters:
            drives = drives.filter(status__iexact=filters['status'])    

        #sorting
        sort_field = sort.get("field", "").strip()  # Clean up any accidental whitespace
        sort_type = sort.get("type", "asc").lower()
        
        ordering = "-created_at"
        if sort_field :
            if sort_field == "company":
                ordering = "company__name"
            elif sort_field == "drive_name":
                ordering = "drive_name"
            elif sort_field == "status":
                ordering = "status"
            elif sort_field == "applicants":
                ordering = "applicants"
            else:
                ordering = "created_at"
        
            if sort_type == "desc":
                ordering = f"-{ordering}"

        drives = drives.order_by(ordering)

        #pagination
        drives, total, pagination = paginate(drives, page, perpage)

        #response
        result = []
        for drive in drives:
            result.append({
                "id": drive.id,
                "company": drive.company.name,
                "drive_name" : drive.drive_name,
                "status": drive.status,
                "applicants":drive.applicants,
                "created_date": drive.created_at.date()
            })
        
        response = {
            "total" : total,
            "pagination" : pagination,
            "data" : result
        }

        return ResponseModel(response,"Success",200)
    
    return ResponseModel(None,"Invalid request method",405)

@permission_required('add_drive','edit_drive')
def drive_dropdowns(request):    
    data = {
        "status": [st for st in DriveStatus]
    }

    return ResponseModel(data,"Drive Dropdowns get successfully",200)

@permission_required('view_drive')
def view_drive(request,id=0):
    drive = get_object_or_404(CompanyDrive,id=id)
    
    job_skills = DriveSkill.objects.filter(drive=drive).select_related("skill")
    job_courses = DriveCourses.objects.filter(drive=drive).select_related("course")
    job_locations = DriveLocation.objects.filter(drive=drive).select_related("city")
    jobs = CompanyDriveJobs.objects.filter(company_drive=drive)

    data={
        "drive_name" : drive.drive_name,
        "ug_package_min" : drive.ug_package_min,
        "ug_package_max" : drive.ug_package_max,
        "pg_package_min" : drive.pg_package_min,
        "pg_package_max" : drive.pg_package_max,
        "stipend":drive.stipend,
        "bond" : drive.bond,
        "minimum_cgpa" : drive.minimum_cgpa,
        "start_date" : drive.start_date.date(),
        "end_date" : drive.end_date.date(),
        "tenth" : drive.tenth,
        "twelth" : drive.twelth,
        "diploma" : drive.diploma,
        "undergraduate" : drive.undergraduate,
        "company" : {
            "value": drive.company.name, 
            "display": drive.company.id.id
        },
        "logo" : drive.company.logo if drive.company.logo else None,
        "status" : {
            "value": [st for st in DriveStatus], 
            "display": drive.status
        },
        "job_type" : {
            "value": [type for type in JobType], 
            "display": drive.job_type
        },
        "job_mode" : {
            "value": [mode for mode in JobMode], 
            "display": drive.job_mode
        },
        "jobs": [
            {"id": j.id,"job_title": j.job_title, "job_description": j.job_description}
            for j in jobs
        ],
        "skills": list({"id":js.skill.id,"name":js.skill.name} for js in job_skills),
        "courses": list({"id":jc.course.id,"name":jc.course.name,"active":jc.course.is_active} for jc in job_courses),  
        "locations": list({"id":jl.city.id,"cityname":jl.city.cityname} for jl in job_locations)   
    } 
 
    return ResponseModel(data,"Drive Fetched Successfully",200)


#jobs frontend structure
# "jobs" :[
#     {
#     "job_title":"this is the job_title",
#     "job_descriprtion" : "yes valid json"
#     },
#     {
#     "job_title":"this is the job_title",
#     "job_descriprtion" : "yes valid json"
#     }
# ]

@permission_required('add_drive')
def add_drive(request):
    if request.method == "POST":
        try:
             # Start a transaction block to ensure all operations succeed or fail together
            with transaction.atomic():
                data = json.loads(request.body)

                company = Company.objects.get(id = data.get("company"))
                job_type_input = data.get("job_type").strip()
                job_mode_input = data.get("job_mode").strip()

                if job_type_input not in JobType.values:
                    raise ValidationError(f"Invalid job_type: '{job_type_input}'. Must be one of {JobType.values}")

                if job_mode_input not in JobMode.values:
                    raise ValidationError(f"Invalid job_mode: '{job_mode_input}'. Must be one of {JobMode.values}")
                
                # print(data.get("company")) 
                try:
                    start_date = datetime.fromisoformat(data.get("start_date").strip())
                    end_date = datetime.fromisoformat(data.get("end_date").strip())
                    start_year = start_date.year

                    if start_date > end_date:
                        return ResponseModel({}, "start date cannot be greater than end date.", 400)
                        
                except ValueError:
                    return ResponseModel({}, "Invalid date format. Use YYYY-MM-DD.", 400)
                
                drive = CompanyDrive(
                    drive_name = data.get("drive_name").strip(),
                    company=company,
                    job_type = data.get("job_type").strip(),
                    job_mode = data.get("job_mode").strip(),
                    ug_package_min = data.get("ug_package_min") or None,
                    ug_package_max = data.get("ug_package_max") or None,
                    pg_package_min = data.get("pg_package_min") or None,
                    pg_package_max = data.get("pg_package_max") or None,
                    stipend = data.get("stipend") or None,
                    bond = data.get("bond","").strip() or None,
                    minimum_cgpa = data.get("minimum_cgpa") or None,
                    start_date = start_date,
                    end_date = end_date,
                    tenth = data.get("tenth") or None,
                    twelth = data.get("twelth") or None,
                    diploma = data.get("diploma") or None,
                    undergraduate = data.get("undergraduate") or None,
                    status = data.get("status").strip()
                )

                drive.full_clean()
                drive.save()

                jobs = data.get("jobs", []) 
                if not jobs or not isinstance(jobs, list):
                   return ResponseModel({}, "At least one job_id must be provided.", 400)
                
                skills = data.get("skills", []) 
                courses = data.get("courses", []) 
                locations = data.get("locations", []) 

                # Prepare JobSkills instances
                job_skills = [DriveSkill(drive_id=drive.id, skill_id=skill_id) for skill_id in skills]
                DriveSkill.objects.bulk_create(job_skills)
                
                job_courses = [DriveCourses(drive_id=drive.id, course_id=course_id) for course_id in courses]
                DriveCourses.objects.bulk_create(job_courses)
                
                job_locations = [DriveLocation(drive_id=drive.id, city_id=city_id) for city_id in locations]
                DriveLocation.objects.bulk_create(job_locations)

                
                skills = Skill.objects.filter(id__in=data.get("skills", [])).values_list('name', flat=True)
                courses = Course.objects.filter(id__in=data.get("courses", [])).values_list('name', flat=True)
                locations = City.objects.filter(id__in=data.get("locations", [])).values_list('cityname', flat=True)

                job_objects=[]
                for job in jobs:                  
                    dJob = CompanyDriveJobs(
                        company_drive_id=drive.id,
                        job_title = job['job_title'],
                        job_description = job['job_description'],
                        posted_date = datetime.now(),
                    )

                    dJob.full_clean()
                    job_objects.append(dJob)

                CompanyDriveJobs.objects.bulk_create(job_objects)


                # Filter valid students (currently studying)
                students = Student.objects.annotate(
                    course_end_year=ExpressionWrapper(
                        F('joining_year') + F('course__years'),
                        output_field=IntegerField()
                    )
                ).filter(
                    joining_year__lte=start_year,
                    course_end_year__gte=start_year,
                    graduation_status='Pursuing'
                )

                # for student in students:
                #     print(student.student_id.email)
                # Launch email sending in a background thread
                threading.Thread(target=send_drive_emails, args=(drive, students, jobs,skills,courses,locations)).start()
                return ResponseModel({},"Drive added successfully!",201)

        except ValidationError as e:
            return ResponseModel({},e.messages,400)

        # except IntegrityError as e:
        #     error_msg = str(e)

        #     # Extract table and key from the message if possible
        #     match = re.search(r'table "(?P<table>[^"]+)" violates foreign key constraint "(?P<constraint>[^"]+)"', error_msg)
        #     detail = re.search(r'DETAIL:  Key \((?P<column>[^)]+)\)=\((?P<value>[^\)]+)\) is not present in table "(?P<ref_table>[^"]+)"', error_msg)

        #     if match and detail:
        #         column = detail.group("column")
        #         value = detail.group("value")
        #         ref_table = detail.group("ref_table")

        #         return ResponseModel(
        #             [],f"Invalid reference: `{column}` with value `{value}` not found in `{ref_table}`.",400)

        #     return ResponseModel([], "A database error occurred.", 500)

        except Exception as e:
            return ResponseModel({},str(e),500)
        
    return ResponseModel({},"Invalid request method",405)

def update_drive_jobs(drive_id, updated_jobs_data):
    existing_jobs = CompanyDriveJobs.objects.filter(company_drive_id=drive_id)
    # 1. Get existing job IDs
    existing_job_ids = set(existing_jobs.values_list("id", flat=True))

    # 2. Separate new jobs and existing job updates
    updated_job_ids = set()
    new_jobs = []

    for job in updated_jobs_data:
        job_id = job.get("id")
        if job_id:
            updated_job_ids.add(job_id)
            # Optionally update existing job fields
            CompanyDriveJobs.objects.filter(id=job_id, company_drive_id=drive_id).update(
                job_title=job.get("job_title"),
                job_description=job.get("job_description"),
            )
        else:
            new_jobs.append(job)

    # 3. Delete jobs that are not in the updated list
    jobs_to_delete = existing_job_ids - updated_job_ids
    CompanyDriveJobs.objects.filter(id__in=jobs_to_delete).delete()

    # 4. Add new jobs
    for job in new_jobs:
        CompanyDriveJobs.objects.create(
            company_drive_id=drive_id,
            job_title=job.get("job_title"),
            job_description=job.get("job_description"),
        )


@permission_required('edit_drive')
def edit_drive(request,id=0):
    if request.method == "POST":
        try: 
            data = json.loads(request.body)
            job_type_input = data.get("job_type").strip()
            job_mode_input = data.get("job_mode").strip()
            if job_type_input not in JobType.values:
                raise ValidationError(f"Invalid job_type: '{job_type_input}'. Must be one of {JobType.values}")
            if job_mode_input not in JobMode.values:
                raise ValidationError(f"Invalid job_mode: '{job_mode_input}'. Must be one of {JobMode.values}")
            
            jobs = data.get("jobs", []) 
            if not jobs or not isinstance(jobs, list):
               return ResponseModel({}, "At least one job_id must be provided.", 400)
            
            # print(data.get("company")) 
            try:
                start_date = datetime.fromisoformat(data.get("start_date").strip())
                end_date = datetime.fromisoformat(data.get("end_date").strip())
                start_year = start_date.year
                if start_date > end_date:
                    return ResponseModel({}, "start date cannot be greater than end date.", 400)
                    
            except ValueError:
                return ResponseModel({}, "Invalid date format. Use YYYY-MM-DD.", 400)

            data = json.loads(request.body)
            drive = get_object_or_404(CompanyDrive,id=id)

            drive.drive_name = data.get("drive_name").strip()
            drive.job_type = data.get("job_type").strip()
            drive.job_mode = data.get("job_mode").strip()
            drive.ug_package_min = data.get("ug_package_min") or None
            drive.ug_package_max = data.get("ug_package_max") or None
            drive.pg_package_min = data.get("pg_package_min") or None
            drive.pg_package_max = data.get("pg_package_max") or None
            drive.stipend = data.get("stipend") or None
            drive.bond = data.get("bond","").strip() or None
            drive.minimum_cgpa = data.get("minimum_cgpa") or None
            drive.start_date = start_date
            drive.end_date = end_date
            drive.tenth = data.get("tenth") or None
            drive.twelth = data.get("twelth") or None
            drive.diploma = data.get("diploma") or None
            drive.undergraduate = data.get("undergraduate") or None
            drive.status = data.get("status").strip()
            drive.save()
            
            update_mapper_by_id(DriveSkill,'drive_id','skill_id',drive.id,data.get('skills',[]))
            update_mapper_by_id(DriveCourses,'drive_id','course_id',drive.id,data.get('courses',[]))
            update_mapper_by_id(DriveLocation,'drive_id','city_id',drive.id,data.get('locations',[]))

            print(drive.id)
            update_drive_jobs(drive.id,jobs)
            print("hjer")
               
            skills = Skill.objects.filter(id__in=data.get("skills", [])).values_list('name', flat=True)
            courses = Course.objects.filter(id__in=data.get("courses", [])).values_list('name', flat=True)
            locations = City.objects.filter(id__in=data.get("locations", [])).values_list('cityname', flat=True)

            # Filter valid students (currently studying)
            students = Student.objects.annotate(
                course_end_year=ExpressionWrapper(
                    F('joining_year') + F('course__years'),
                    output_field=IntegerField()
                )
            ).filter(
                joining_year__lte=start_year,
                course_end_year__gte=start_year,
                graduation_status='Pursuing'
            )

            threading.Thread(target=send_drive_emails, args=(drive, students, jobs,skills,courses,locations,True)).start()

            return ResponseModel({},"Drive updated successfully",200)
        
        except Company.DoesNotExist:
            return ResponseModel({},"Drive not found",404)
        except Exception as e:
            return ResponseModel({},str(e),500)
        
    return ResponseModel({},"Invalid request method", 405)


@permission_required('delete_drive')
def delete_drive(request,id=0):
    if request.method == "DELETE":
        try:
            with transaction.atomic():
                drive = get_object_or_404(CompanyDrive, id=id)

                # Check for drive mapping
                if DriveApplication.objects.filter(drive=drive).exists():
                    return ResponseModel({},"You can't delete the drive because it has applicants",400)
                
                # Check for PlacementOffer mapping
                if PlacementOffer.objects.filter(job__company_drive=drive).exists():
                        return ResponseModel({},"You can't delete drive which have associated placement data",400)
                
                # Delete company 
                drive.delete()

                return ResponseModel({},"Drive deleted successfully",200)
        
        except Exception as e:
            return ResponseModel({},str(e),500)


    return ResponseModel({},"Invalid request method",400)
