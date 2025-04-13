from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from ..schema.companies import  Company,CompanySize,CompanyType,Category
from ..schema.users import User
from ..schema.industry import Industry
from ..schema.cities import City
from ..schema.job_positions import JobPosition
from ..schema.company_drive_jobs import CompanyDriveJobs
from ..schema.company_drives import CompanyDrive
from ..utils.random_password_utils import generate_random_password
from ..decorators import permission_required
from django.contrib.auth.hashers import make_password
from ..schema.user_roles import UserRole
from ..schema.roles import Role
from django.db import transaction
from ..utils.email_utils import send_registration_email 
from django.db.models import Q,When,Case,CharField,Value
from ..utils.helper_utils import safe_value,safe_deep_get,paginate,ResponseModel,validate_pagination
from django.views.decorators.csrf import csrf_exempt
import json

@permission_required('register_company')
def register_company(request):
    if request.method == "POST":
        password = None
        try:
             # Start a transaction block to ensure all operations succeed or fail together
            with transaction.atomic():
                data = request.POST
                logo = request.FILES.get("logo") 
                password  = generate_random_password()
                # print(password)
                #firstly user creation
                user = User(
                    email = data.get("email"),
                    password = make_password(password),
                    phone = data.get("phone")
                )
                user.save()

                #after than company creation 
                industry = Industry.objects.get(id=data.get("industry"))
                city = City.objects.get(id=data.get("headquater"))
                position = JobPosition.objects.get(id=data.get("contact_person_position"))
    
                company = Company(
                    id=user,
                    name=data.get("name").strip(),
                    website=data.get("website", "").strip() or None,
                    founded_year=data.get("founded_year"),
                    category=data.get("category"),
                    industry=industry,
                    company_size=data.get("company_size"),
                    company_type=data.get("company_type"),
                    headquater=city,
                    contact_person_name=data.get("contact_person_name", "").strip() or None,
                    contact_person_email=data.get("contact_person_email", "").strip() or None,
                    contact_person_position=position,
                    address=data.get("address", "").strip() or None,
                    logo=logo,  # Save uploaded file
                )

                company.save()

                role = Role.objects.filter(name='Company').first()
                if not role:
                    raise ValidationError("Role 'Company' does not exist.")

                user_role = UserRole(user = user,role = role)
                user_role.save()

                send_registration_email(user.email,password)

                return ResponseModel({},"Company added successfully!",201)

        except ValidationError as e:
            return ResponseModel({},e.message,400)
        
        except Exception as e:
            return ResponseModel({},str(e),500)
        
    return ResponseModel({},"Invalid request method",405)

# @permission_required('register_company','edit_company')
# def company_dropdowns(request):
#     data = {
#         "industries": list(Industry.objects.values("id", "name")),
#         "positions": list(JobPosition.objects.values("id", "name")),
#         "company_sizes": [
#             {"value": size.value, "label": size.label} for size in CompanySize
#         ],
#         "company_types": [
#             {"value": ctype.value, "label": ctype.label} for ctype in CompanyType
#         ],
#         "categories": [
#             {"value": cat.value, "label": cat.label} for cat in Category
#         ]
#     }

#     return ResponseModel(data,"Dropdowns Get Succesfully",200)

@permission_required('view_company')
def view_company(request,id=0):
    company = get_object_or_404(Company,id=id)
    user = company.id

    data={
        "id" : user.id,
        "name" : company.name,
        "email" : company.id.email,
        "phone" : company.id.phone,
        "website" : company.website ,
        "founded_year" : company.founded_year,
        "category" : {
            "value": company.category, 
            "display": company.get_category_display()
        },
        "industry" :{
            "value": safe_value(company.industry, "id"),
            "display": safe_value(company.industry, "name"),
        } ,
        "company_size" : {
            "value": company.company_size, 
            "display": company.get_company_size_display()
        },
        "company_type" : {
            "value": company.company_type, 
            "display": company.get_company_type_display()
        },
        "headquater" : {
            "value": safe_value(company.headquater, "id"), 
            "display": safe_value(company.headquater, "cityname"),
            "country_id":safe_deep_get(company.headquater,"state.country.id")
        } ,
        "contact_person_name" : company.contact_person_name ,
        "contact_person_email" : company.contact_person_email,
        "contact_person_position" : {
            "value": safe_value(company.contact_person_position, "id"),
            "display": safe_value(company.contact_person_position, "name"),
        } ,
        "address" : company.address,
        "logo" : company.logo if company.logo else None
    } 
 
    return ResponseModel(data,"Company Fetched Successfully",200)


# Frontend Structure
# {
#     "filters": {
#         "industry" : 2,
#         "search": "company"
#     },
#     "sort": {  "field": "company_type", "type": "asc"},
#     "page" : 1,
#     "perpage":10
# }

@permission_required('view_companies')  
def list_companies(request):
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
        companies = Company.objects.select_related("industry")

        # companies = companies.annotate(
        #     company_type_label=Case
        #     (
        #         *[When(company_type=value, then=Value(label)) for value, label in CompanyType.choices],
        #         output_field=CharField()
        #     )
        # )

        # filtering
        if search := data.get("search","").strip():
            companies = companies.filter(Q(name__icontains=search) | Q(id__email__icontains=search))
        
        if industry:= data.get("industry","").strip():
            companies = companies.filter(industry=industry)

        if company_size:= data.get("company_size","").strip():
            companies = companies.filter(company_size=company_size)

        #sorting
        sort_field = sort.get("field", "").strip()  # Clean up any accidental whitespace
        sort_type = sort.get("type", "asc").lower()
        
        ordering = "name"
        if sort_field :
            if sort_field == "industry":
                ordering = "industry__name"
            elif sort_field == "company_size":
                ordering = "company_size"
            elif sort_field == "email":
                ordering = "id__email"
            elif sort_field == "phone":
                ordering = "id__phone"
            # elif sort_field == "company_type":
            #     ordering = "company_type_label"
            else:
                ordering= "name"

            if sort_type == "desc":
                ordering = f"-{ordering}"

        companies = companies.order_by(ordering)

        #pagination
        companies, total, pagination = paginate(companies, page, perpage)

        result = []
        for company in companies:
            result.append({
                "id": company.id.id,
                "name": company.name,
                "email": company.id.email,
                "phone": company.id.phone,
                "company_size": company.get_company_size_display(),
                "industry": safe_value(company.industry,"name")
                # "company_type": company.get_company_type_display()
            })
        filter_options={      
            "industries": list(Industry.objects.values("id", "name")),
            "company_sizes": [
                {"value": size.value, "label": size.label} for size in CompanySize
            ],
         }
        # response={
        #     "data":result,
        #     "total":total,
        #     "pagination":pagination
        # } 
        return render(request, "companies_list.html", {
        "data": result,
        "total": total,
        "pagination": pagination,
        "filter_options": filter_options
        })

    return ResponseModel({},"Invalid request method", 405)


@permission_required('edit_company')
def edit_company(request,id=0):
    if request.method == "POST":
        try:
            company = get_object_or_404(Company,id=id)
            data = request.POST
            # Update fields
            company.name = data.get("name", company.name).strip()
            company.website = data.get("website", company.website).strip()
            company.founded_year=data.get("founded_year")
            company.category = data.get("category")
            company.id.email = data.get("email", company.id.email).strip()
            company.id.phone = data.get("phone", company.id.phone)
            company.company_size = data.get("company_size", company.company_size)
            company.company_type = data.get("company_type", company.company_type)
            company.contact_person_name = data.get("contact_person_name", company.contact_person_name).strip()
            company.contact_person_email = data.get("contact_person_email", company.contact_person_email).strip()
            company.address = data.get("address", company.address).strip()

            industry_id = data.get("industry")
            if industry_id:
                company.industry = Industry.objects.get(id=industry_id)

            hq_id = data.get("headquater")
            if hq_id:
                company.headquater = City.objects.get(id=hq_id)
            
            contact_pos_id = data.get("contact_person_position")
            if contact_pos_id:
                company.contact_person_position = JobPosition.objects.get(id=contact_pos_id)

            if "logo" in request.FILES:
                company.logo = request.FILES["logo"]

            company.id.save()
            company.save()

            return ResponseModel({},"Company updated successfully",200)
        
        except Company.DoesNotExist:
            return ResponseModel({},"Company not found",404)
        except Exception as e:
            return ResponseModel({},str(e),500)
        
    return ResponseModel({},"Invalid request method", 405)

@permission_required('delete_company')
def delete_company(request,id=0):
    if request.method == "DELETE":
        try:
            with transaction.atomic():
                company = get_object_or_404(Company, id=id)
                user = company.id

                # Check for assigned jobs
                # if Job.objects.filter(company=company).exists():
                #     return ResponseModel({},"Cannot delete company with assigned jobs",400)
                
                # Check for company_drive mapping
                if CompanyDrive.objects.filter(company=company).exists():
                        return ResponseModel({},"Cannot delete company mapped in company_drive",400)
                
                # Delete company 
                company.delete()
                user.delete()

                return ResponseModel({},"Company deleted successfully",200)
        
        except Exception as e:
            return ResponseModel({},str(e),500)


    return ResponseModel({},"Invalid request method",400)

def get_industries(request):
    industries = list(Industry.objects.values("id", "name").order_by("name"))
    return ResponseModel(industries,"Industries Fetch Succesfully",200)
    