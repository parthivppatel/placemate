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
from django.urls import reverse
from ..decorators import permission_required
from ..utils.email_utils import send_registration_email,send_drive_emails
from django.db.models import Q,Count, F, ExpressionWrapper, IntegerField
from ..utils.helper_utils import safe_value,safe_deep_get,paginate,ResponseModel,update_mapper_by_id,validate_pagination
from ..utils.jwt_utils import has_permission,get_user_from_jwt
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction,IntegrityError
import json
import threading
import re
from datetime import datetime

def get_drives_context():
    return {
        "companies": list(Company.objects.values("id", "name")),
        "courses_dropdown": list(Course.objects.values("id", "name")),
        "skills_dropdown": list(Skill.objects.values("id", "name")),
        "job_types": [type.value for type in JobType],
        "job_modes": [mode.value for mode in JobMode],
        "status_dropdown" : [mode.value for mode in DriveStatus]
    }


@permission_required('add_drive')
def add_drive_page(request):
    context = get_drives_context()
    return render(request,'add_drive.html',context)

@permission_required('view_drives')   
def list_drives(request):
    page,perpage = 1,10
    if request.method == "GET":
        data = request.GET
        # filters = data.get("filters", {})
        sort = data.get("sort", {})
        validate_pg = validate_pagination(data)
        if validate_pg is None:
            return ResponseModel({},"Page and perpage must be valid positive integers", 400)
        page, perpage = validate_pg

        # data gathering
        drives = CompanyDrive.objects.select_related("company").annotate(
            applicants=Count("driveapplication")
        )

        # filtering
        if search := data.get("search","").strip():
            drives = drives.filter(Q(drive_name__icontains=search) | Q(company__name__icontains=search))

        if status := data.get("status","").strip():
            drives = drives.filter(status__iexact=status)    

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
                "job_type" : drive.job_type,
                "job_mode" : drive.job_mode,
                "start_date" : drive.start_date,
                "status": drive.status,
                "applicants":drive.applicants,
            })
        
        filter_options={      
            "status_dropdown": [
                {"value": status.value} for status in DriveStatus
            ],
        }

        # Check if the user has the 'add_students' and 'delete_students' permissions
        user_payload = get_user_from_jwt(request)
        user_role = user_payload.get("role") if user_payload else None
        add_drive = has_permission(user_role, 'add_drive')
        view_drive = has_permission(user_role, 'view_drive')
        delete_drive = has_permission(user_role, 'delete_drive')

        return render(request, "drives_list.html", {
            "data": result,
            "total": total,
            "pagination": pagination,
            "filter_options": filter_options,
            "permissions":{
                "add_drive" : add_drive,
                "view_drive" : view_drive,
                "delete_drive" : delete_drive
            }
        })
    
    messages.error(request,"Invalid request method")
    return redirect("dashboard")

@permission_required('edit_drive')   
def edit_drive_page(request,id=0):
    url = reverse('view_drive', kwargs={'id': id}) + "?mode=edit"
    return redirect(url)

@permission_required('view_drive','edit_drive')
def view_drive(request,id=0):
    drive = get_object_or_404(CompanyDrive,id=id)
    mode = request.GET.get('mode', 'view')

    job_skills = DriveSkill.objects.filter(drive=drive).select_related("skill")
    job_courses = DriveCourses.objects.filter(drive=drive).select_related("course")
    job_locations = DriveLocation.objects.filter(drive=drive).select_related("city")
    jobs = CompanyDriveJobs.objects.filter(company_drive=drive)

    s_ids = [js.skill.id for js in job_skills]
    s_names = [js.skill.name for js in job_skills]

    c_ids = [jc.course.id for jc in job_courses]
    c_names = [jc.course.name for jc in job_courses]

    # Check if the user has the 'add_students' and 'delete_students' permissions
    user_payload = get_user_from_jwt(request)
    user_role = user_payload.get("role") if user_payload else None
    edit_drive = has_permission(user_role, 'edit_drive')

    data={
        "id":drive.id,
        "drive_name" : drive.drive_name,
        "ug_package_min" : drive.ug_package_min,
        "ug_package_max" : drive.ug_package_max,
        "pg_package_min" : drive.pg_package_min,
        "pg_package_max" : drive.pg_package_max,
        "stipend":drive.stipend,
        "bond" : drive.bond,
        "minimum_cgpa" : drive.minimum_cgpa,
        "start_date" : drive.start_date,
        "end_date" : drive.end_date,
        "tenth" : drive.tenth,
        "twelth" : drive.twelth,
        "diploma" : drive.diploma,
        "undergraduate" : drive.undergraduate,
        "company" : {
            "value": drive.company.name, 
            "display": drive.company.id.id
        },
        "logo" : drive.company.logo if drive.company.logo else None,
        "status" : drive.status,
        "job_type" :drive.job_type,        
        "created_at":drive.created_at,
        "job_mode" : drive.job_mode,
        "jobs": [
            {"id": j.id,"job_title": j.job_title, "job_description": j.job_description}
            for j in jobs
        ],
        "skills": {
            'ids':s_ids,
            'names':s_names
        },
        "courses": {
            'ids' : c_ids,
            'names' : c_names
        },  
        "locations": list({"id":jl.city.id,"cityname":jl.city.cityname} for jl in job_locations),
        "edit_drive":edit_drive
    } 

    if(mode == 'edit'):
        context = get_drives_context()
        data.update(context)

        return render(request,'edit_drive.html',data)
    
    return render(request,'view_drive.html',data)
    # return ResponseModel(data,"Drive Fetched Successfully",200)


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
def sanitize_data(data):
    def sanitize_value(value):
        # Strip strings, return None if empty
        if isinstance(value, str):
            return value.strip() if value.strip() != '' else None
        
        # If it's a list, handle items recursively
        elif isinstance(value, list):
            return [sanitize_value(item) for item in value]
        
        # If it's a dictionary (object), recurse
        elif isinstance(value, dict):
            return {key: sanitize_value(val) for key, val in value.items()}
        
        # For other data types (numbers, booleans, etc.), return the value unchanged
        else:
            return value

    # Apply sanitization to all keys/values in the dictionary
    return {key: sanitize_value(value) for key, value in data.items()}

def validate_drive_data(data,is_edit=False):
    def is_invalid_int(value):
        try:
            return int(value) < 0
        except (ValueError, TypeError):
            return True
    
    # Validate required fields
    required_fields = ['drive_name', 'job_type', 'job_mode','start_date','end_date']
    if not is_edit:
        required_fields.append('company')
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    jobs = data.get('jobs', [])
    for i,job in enumerate(jobs):
        job_title = job.get("job_title")
        job_description = job.get("job_description")
        if not job_title or not job_description:
            return False, f"Missing job_title or job_description in job {i + 1}"

    # Integer Checking
    int_fields=["minimum_cgpa", "ug_package_min", "ug_package_max", "pg_package_min", "pg_package_max","stipend","tenth","twelth","diploma","undergraduate"]
    for field in int_fields:
        value = data.get(field)
        if value not in [None, '', 'null'] and is_invalid_int(value):
            return False, f"{field.replace('_', ' ').capitalize()} must be a positive integer."
    
    job_type = data.get("job_type")
    job_mode = data.get("job_mode")
    status = data.get("status")

    try:
        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date"))

        if start_date >= end_date:
            return False, "Start date cannot be greater than equal to end date."
                        
    except ValueError:
        return False, "Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS."

    if (data.get("ug_package_min") and data.get("ug_package_max")) and data["ug_package_min"]> data["ug_package_max"]:
        return False, "UG package min must not be greater than UG package max."

    if (data.get("pg_package_min") and data.get("pg_package_max")) and data["pg_package_min"]> data["pg_package_max"]:
        return False, "PG package min must not be greater than PG package max."

    if job_type not in JobType.values:
        return False, f"Invalid job_type: '{job_type}'. Must be one of {JobType.values}"

    if job_mode not in JobMode.values:
        return False, f"Invalid job_mode: '{job_mode}'. Must be one of {JobMode.values}"
                
    if status not in DriveStatus.values:
        return False, f"Invalid status: '{status}'. Must be one of {DriveStatus.values}"
    return True, "Validated successfully"



@permission_required('add_drive')
def add_drive(request):
    if request.method == "POST":
        data = json.loads(request.body)
    
        # for key,value in request.POST:
        #     print("hwllo")
        #     print("key",key)
        #     print("value",value)
        data = sanitize_data(data)
        is_valid, message = validate_drive_data(data)
        if not is_valid:
            return ResponseModel({}, message, 400)
        
        try:
             # Start a transaction block to ensure all operations succeed or fail together
            with transaction.atomic():
                company = Company.objects.get(id = data.get("company"))
                
                # print(data.get("company")) 
                start_date = datetime.fromisoformat(data.get("start_date"))
                end_date = datetime.fromisoformat(data.get("end_date"))
                start_year = start_date.year                        
                
                drive = CompanyDrive(
                    drive_name = data.get("drive_name"),
                    company=company,
                    job_type = data.get("job_type"),
                    job_mode = data.get("job_mode"),
                    ug_package_min = data.get("ug_package_min") or None,
                    ug_package_max = data.get("ug_package_max") or None,
                    pg_package_min = data.get("pg_package_min") or None,
                    pg_package_max = data.get("pg_package_max") or None,
                    tenth = data.get("tenth") or None,
                    twelth = data.get("twelth") or None,
                    diploma = data.get("diploma") or None,
                    undergraduate = data.get("undergraduate") or None,
                    stipend = data.get("stipend") or None,
                    bond = data.get("bond") or None,
                    minimum_cgpa = data.get("minimum_cgpa") or None,
                    start_date = start_date,
                    end_date = end_date,
                    status = data.get("status")
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
                messages.success(request,"Drive added successfully")
                return ResponseModel({},"Drive added successfully!!",201)

        except CompanyDrive.DoesNotExist:
            return ResponseModel({},"Company Not found!",400)
        except ValidationError as e:
            for field, error_list in e.message_dict.items():
                for err in error_list:
                    return ResponseModel({},f"{field.replace('_', ' ').capitalize()}: {err}",400)
            return ResponseModel({},e.messages,400)

        except IntegrityError as e:
            error_msg = str(e)

            # Extract table and key from the message if possible
            match = re.search(r'table "(?P<table>[^"]+)" violates foreign key constraint "(?P<constraint>[^"]+)"', error_msg)
            detail = re.search(r'DETAIL:  Key \((?P<column>[^)]+)\)=\((?P<value>[^\)]+)\) is not present in table "(?P<ref_table>[^"]+)"', error_msg)

            if match and detail:
                column = detail.group("column")
                value = detail.group("value")
                ref_table = detail.group("ref_table")

                return ResponseModel(
                    [],f"Invalid reference: `{column}` with value `{value}` not found in `{ref_table}`.",400)

            return ResponseModel([], "A database error occurred.", 500)

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
        data = json.loads(request.body)
        data = sanitize_data(data)
        is_valid, message = validate_drive_data(data,True)
        if not is_valid:
            return ResponseModel({}, message, 400)

        try: 
            drive = CompanyDrive.objects.get(id=id)
            start_date = datetime.fromisoformat(data.get("start_date"))
            end_date = datetime.fromisoformat(data.get("end_date"))
            start_year = start_date.year    

            drive.drive_name = data.get("drive_name")
            drive.job_type = data.get("job_type")
            drive.job_mode = data.get("job_mode")
            drive.ug_package_min = data.get("ug_package_min") or None
            drive.ug_package_max = data.get("ug_package_max") or None
            drive.pg_package_min = data.get("pg_package_min") or None
            drive.pg_package_max = data.get("pg_package_max") or None
            drive.stipend = data.get("stipend") or None
            drive.bond = data.get("bond") or None
            drive.minimum_cgpa = data.get("minimum_cgpa") or None
            drive.start_date = start_date
            drive.end_date = end_date
            drive.tenth = data.get("tenth") or None
            drive.twelth = data.get("twelth") or None
            drive.diploma = data.get("diploma") or None
            drive.undergraduate = data.get("undergraduate") or None
            drive.status = data.get("status")
            drive.save()

            update_mapper_by_id(DriveSkill,'drive_id','skill_id',drive.id,data.get('skills',[]))
            update_mapper_by_id(DriveCourses,'drive_id','course_id',drive.id,data.get('courses',[]))
            update_mapper_by_id(DriveLocation,'drive_id','city_id',drive.id,data.get('locations',[]))

            jobs = data.get("jobs", []) 
            if not jobs or not isinstance(jobs, list):
                return ResponseModel({}, "At least one job_id must be provided.", 400)
            # print(drive.id)
            update_drive_jobs(drive.id,jobs)
               
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
            
            messages.success(request,"Drive updated successfully")
            return ResponseModel({},"Drive updated successfully",200)
        
        except CompanyDrive.DoesNotExist:
            return ResponseModel({},"Drive not found",404)
        except ValidationError as e:
            for field, error_list in e.message_dict.items():
                for err in error_list:
                    return ResponseModel({},f"{field.replace('_', ' ').capitalize()}: {err}",400)
            return ResponseModel({},e.messages,400)

        except IntegrityError as e:
            error_msg = str(e)

            # Extract table and key from the message if possible
            match = re.search(r'table "(?P<table>[^"]+)" violates foreign key constraint "(?P<constraint>[^"]+)"', error_msg)
            detail = re.search(r'DETAIL:  Key \((?P<column>[^)]+)\)=\((?P<value>[^\)]+)\) is not present in table "(?P<ref_table>[^"]+)"', error_msg)

            if match and detail:
                column = detail.group("column")
                value = detail.group("value")
                ref_table = detail.group("ref_table")

                return ResponseModel(
                    [],f"Invalid reference: `{column}` with value `{value}` not found in `{ref_table}`.",400)

            return ResponseModel([], "A database error occurred.", 500)

        except Exception as e:
            return ResponseModel({},str(e),500)
        
    return ResponseModel({},"Invalid request method", 405)


@permission_required('delete_drive')
def delete_drive(request):
    if request.method == "POST":
        drive_id = request.POST.get("drive_id")
        if not drive_id:
            messages.error(request, "drive id is required to delete.")
            return redirect("list_drives")
        try:
            with transaction.atomic():
                drive = CompanyDrive.objects.get(id=drive_id)

                # Check for drive mapping
                if DriveApplication.objects.filter(drive=drive).exists():
                    messages.error(request,"You can't delete the drive because it has applicants")
                    return redirect("list_drives")                
                # Check for PlacementOffer mapping
                if PlacementOffer.objects.filter(job__company_drive=drive).exists():
                    messages.error(request,"You can't delete drive which have associated placement data")
                    return redirect("list_drives")

                # Delete company 
                drive.delete()

                messages.success(request,"Drive deleted successfully")
                return redirect("list_drives")
            
        except CompanyDrive.DoesNotExist:
            messages.error(request,"Company Drive not found")
            return redirect("list_drives")
        except Exception as e:
            messages.error(request,str(e))
            return redirect('list_drives')
        
    messages.error(request,"Invalid request method")
    return redirect('list_drives')