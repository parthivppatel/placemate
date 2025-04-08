from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from ..schema.jobs import Job,JobType,JobMode
from ..schema.companies import Company
from ..schema.job_skills import JobSkill
from ..schema.job_courses import JobCourses
from ..schema.job_locations import JobLocation
from ..schema.company_drive_jobs import CompanyDriveJobs
from ..schema.placement_offers import PlacementOffer 
from ..utils.random_password_utils import generate_random_password
from ..decorators import permission_required
from ..utils.email_utils import send_registration_email 
from django.db.models import Q
from ..utils.helper_utils import safe_value,safe_deep_get,paginate,ResponseModel,update_mapper_by_id
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction,IntegrityError
import json
import re
from datetime import datetime


@permission_required('view_jobs')   
def list_jobs(request):
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
        jobs = Job.objects.select_related("company")

        # filtering
        if search := filters.get("search","").strip():
            jobs = jobs.filter(Q(job_title__icontains=search) | Q(company__name__icontains=search))

        if "job_type" in filters:
            jobs = jobs.filter(job_type__iexact=filters['job_type'])

        if "job_mode" in filters:
            jobs = jobs.filter(job_mode__iexact=filters['job_mode'])
        
        if "company" in filters:  
            jobs = jobs.filter(company__exact = filters['company'])
        
        if "posted_date" in filters:
            try:
                from_date = datetime.strptime(filters['posted_date'][0], "%Y-%m-%d").date()
                to_date = datetime.strptime(filters['posted_date'][1], "%Y-%m-%d").date()

                if from_date > to_date:
                    return ResponseModel({}, "From date cannot be greater than To date.", 400)
                jobs = jobs.filter(posted_date__date__range=(from_date, to_date))

            except ValueError:
                return ResponseModel({}, "Invalid date format. Use YYYY-MM-DD.", 400)

        #sorting
        sort_field = sort.get("field", "").strip()  # Clean up any accidental whitespace
        sort_type = sort.get("type", "asc").lower()
        
        ordering = "-posted_date"
        if sort_field :
            if sort_field == "company":
                ordering = "company__name"
            elif sort_field == "job_title":
                ordering = "job_title"
            elif sort_field == "job_type":
                ordering = "job_type"
            elif sort_field == "job_mode":
                ordering = "job_mode"
            else:
                ordering = "posted_date"
        
            if sort_type == "desc":
                ordering = f"-{ordering}"

        jobs = jobs.order_by(ordering)

        #pagination
        jobs, total, pagination = paginate(jobs, page, perpage)

        #response
        result = []
        for job in jobs:
            result.append({
                "id": job.id,
                "company": job.company.name,
                "job_title": job.job_title,
                "job_type": job.job_type,
                "job_mode": job.job_mode,
                "posted_date": job.posted_date.date()
            })
        
        response = {
            "data" : result,
            "total" : total,
            "pagination" : pagination
        }

        return ResponseModel(response,"Success",200)
    
    return ResponseModel(None,"Invalid request method",405)

@permission_required('post_job','edit_job')
def job_dropdowns(request):    
    data = {
        "companies": list(Company.objects.values("id", "name")),
        "job_type": [type for type in JobType],
        "job_mode": [mode for mode in JobMode]
    }

    return ResponseModel(data,"Job Dropdowns get successfully",200)

@permission_required('view_job')
def view_job(request,id=0):
    job = get_object_or_404(Job,id=id)
    
    job_skills = JobSkill.objects.filter(job=job).select_related("skill")
    job_courses = JobCourses.objects.filter(job=job).select_related("course")
    job_locations = JobLocation.objects.filter(job=job).select_related("city")

    data={
        "job_title" : job.job_title,
        "job_description" : job.job_description,
        "salary_package_min" : job.salary_package_min,
        "salary_package_max" : job.salary_package_max,
        "bond" : job.bond,
        "minimum_cgpa" : job.minimum_cgpa ,
        "posted_date" : job.posted_date.date(),
        "tenth" : job.tenth,
        "twelth" : job.twelth,
        "diploma" : job.diploma,
        "undergraduate" : job.diploma,
        "company" : {
            "value": job.company.name, 
            "display": job.company.id.id
        },
        "logo" : job.company.logo if job.company.logo else None,
        "job_type" : {
            "value": [type for type in JobType], 
            "display": job.job_type
        },
        "job_mode" : {
            "value": [mode for mode in JobMode], 
            "display": job.job_mode
        },
        "skills": list({"id":js.skill.id,"name":js.skill.name} for js in job_skills),
        "courses": list({"id":jc.course.id,"name":jc.course.name,"active":jc.course.is_active} for jc in job_courses),  
        "locations": list({"id":jl.city.id,"cityname":jl.city.cityname} for jl in job_locations)   
    } 
 
    return ResponseModel(data,"Job Fetched Successfully",200)

@permission_required('post_job')
def post_job(request):
    if request.method == "POST":
        try:
             # Start a transaction block to ensure all operations succeed or fail together
            with transaction.atomic():
                data = json.loads(request.body)
                # print(data.get("company"))
                company = Company.objects.get(id = data.get("company"))
            
                job = Job(
                    company=company,
                    job_title = data.get("job_title").strip(),
                    job_description = data.get("job_description").strip(),
                    job_type = data.get("job_type").strip(),
                    job_mode = data.get("job_mode").strip(),
                    salary_package_min = data.get("salary_package_min").strip(),
                    salary_package_max = data.get("salary_package_max").strip(),
                    bond = data.get("bond","").strip() or None,
                    minimum_cgpa = data.get("minimum_cgpa","").strip() or None,
                    posted_date = datetime.now(),
                    tenth = data.get("tenth","").strip() or None,
                    twelth = data.get("twelth","").strip() or None,
                    diploma = data.get("minimum_cgpa","").strip() or None,
                    undergraduate = data.get("minimum_cgpa","").strip() or None,
                )

                job.save()

                skills = data.get("skills", []) 
                courses = data.get("courses", []) 
                locations = data.get("locations", []) 

                # Prepare JobSkills instances
                job_skills = [JobSkill(job_id=job.id, skill_id=skill_id) for skill_id in skills]
                JobSkill.objects.bulk_create(job_skills)
                
                job_courses = [JobCourses(job_id=job.id, course_id=course_id) for course_id in courses]
                JobCourses.objects.bulk_create(job_courses)
                
                job_locations = [JobLocation(job_id=job.id, city_id=city_id) for city_id in locations]
                JobLocation.objects.bulk_create(job_locations)

                return ResponseModel({},"Job added successfully!",201)

        except ValidationError as e:
            return ResponseModel({},e.message,400)

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


@permission_required('edit_job')
def edit_job(request,id=0):
    if request.method == "POST":
        try:
            job = get_object_or_404(Job,id=id)
            data = json.loads(request.body)

            job.job_title = data.get("job_title").strip()
            job.job_description = data.get("job_description").strip()
            job.job_type = data.get("job_type").strip()
            job.job_mode = data.get("job_mode").strip()
            job.salary_package_min = data.get("salary_package_min").strip()
            job.salary_package_max = data.get("salary_package_max").strip()
            job.bond = data.get("bond","").strip() or None
            job.minimum_cgpa = data.get("minimum_cgpa","").strip() or None
            job.updated_date = datetime.now()
            job.tenth = data.get("tenth","").strip() or None
            job.twelth = data.get("twelth","").strip() or None
            job.diploma = data.get("minimum_cgpa","").strip() or None
            job.undergraduate = data.get("minimum_cgpa","").strip() or None
            job.save()
            
            update_mapper_by_id(JobSkill,'job_id','skill_id',job.id,data.get('skills',[]))
            update_mapper_by_id(JobCourses,'job_id','course_id',job.id,data.get('courses',[]))
            update_mapper_by_id(JobLocation,'job_id','city_id',job.id,data.get('locations',[]))

            return ResponseModel({},"Job updated successfully",200)
        
        except Company.DoesNotExist:
            return ResponseModel({},"Job not found",404)
        except Exception as e:
            return ResponseModel({},str(e),500)
        
    return ResponseModel({},"Invalid request method", 405)


@permission_required('delete_job')
def delete_job(request,id=0):
    if request.method == "DELETE":
        try:
            with transaction.atomic():
                job = get_object_or_404(Job, id=id)

                # Check for drive mapping
                if CompanyDriveJobs.objects.filter(job=job).exists():
                    return ResponseModel({},"Cannot delete Job which have drive created",400)
                
                # Check for PlacementOffer mapping
                if PlacementOffer.objects.filter(job=job).exists():
                        return ResponseModel({},"Cannot delete Job in which student get offered",400)
                
                # Delete company 
                job.delete()

                return ResponseModel({},"Job deleted successfully",200)
        
        except Exception as e:
            return ResponseModel({},str(e),500)


    return ResponseModel({},"Invalid request method",400)
