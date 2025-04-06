from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from ..schema.companies import  Company,CompanySize,CompanyType,Category
from ..schema.job_positions import JobPosition
from ..schema.jobs import Job
from ..utils.random_password_utils import generate_random_password
from ..decorators import permission_required
from ..utils.email_utils import send_registration_email 
from django.db.models import Q,When,Case,CharField,Value
from ..utils.helper_utils import safe_value,safe_deep_get,paginate,ResponseModel
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime


# @permission_required('view_companies')       
def list_jobs(request):
    if request.method == "POST":
        data = json.loads(request.body)
        filters = data.get("filters", {})
        sort = data.get("sort", {})
        try:
            page = int(data.get("page", 1))
            perpage = int(data.get("perpage", 10))

            if page < 1 or perpage < 1:
                return ResponseModel([],"Page and per page must be positive integers",400)
        except:
            return ResponseModel([],"Page and per page must be valid integers.",400)


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
                    return ResponseModel([], "From date cannot be greater than To date.", 400)
                jobs = jobs.filter(posted_date__date__range=(from_date, to_date))

            except ValueError:
                return ResponseModel([], "Invalid date format. Use YYYY-MM-DD.", 400)

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

        return ResponseModel(result,"Success",200,pagination,total)
    
    return ResponseModel(None,"Invalid request method", 405)

