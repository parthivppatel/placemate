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
from django.urls import reverse
from ..schema.roles import Role
from django.db import transaction
from ..utils.email_utils import send_registration_email 
from ..utils.jwt_utils import has_permission,get_user_from_jwt
from django.db.models import Q,When,Case,CharField,Value
from ..utils.helper_utils import safe_value,safe_deep_get,paginate,ResponseModel,validate_pagination
from django.views.decorators.csrf import csrf_exempt
import json
import time

def get_company_registration_context():
    return {
        "industries": list(Industry.objects.values("id", "name")),
        "positions": list(JobPosition.objects.values("id", "name")),
        "company_sizes": [
            {"value": size.value, "label": size.label} for size in CompanySize
        ],
        "company_types": [
            {"value": ctype.value, "label": ctype.label} for ctype in CompanyType
        ],
        "categories": [
            {"value": cat.value, "label": cat.label} for cat in Category
        ],
        "header_title":"Register New Company",
        "header_subtitle":"Add a new company to the placemate",
        "button": "Register Company"
    }

@permission_required('register_company')
def company_registration_page(request):
    context = get_company_registration_context()
    return render(request,'company_registration.html',context)


def validate_company_data(request,data,edit=False,id=0):
    def redirect_with_context():
        context = get_company_registration_context()
        if edit:
            return redirect("edit_company_page", id=id)
        return render(request, "company_registration.html", context)
    
    def is_invalid_int(value):
        try:
            return int(value) < 0
        except (ValueError, TypeError):
            return True
    
    # Validate required fields
    required_fields = ['email', 'phone', 'name','category','headquater']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        messages.error(request, f"Missing required fields: {', '.join(missing_fields)}")
        return redirect_with_context()
    
    # Integer Checking
    int_fields=["founded_year", "company_size", "company_type", "industry", "contact_person_position"]
    for field in int_fields:
        value = data.get(field)
        if value not in [None, '', 'null'] and is_invalid_int(value):
            messages.error(request, f"{field.replace('_', ' ').capitalize()} must be a positive integer.")
            return redirect_with_context()
    # Uniqueness validation helper
    def check_unique(model, fields_dict, label):
        for field, value in fields_dict.items():
            if not value:
                continue
            queryset = model.objects.filter(**{field: value})
            if edit:
                queryset = queryset.exclude(id=id)
            if queryset.exists():
                messages.error(request, f"{label} with {field.replace('_', ' ')} '{value}' already exists.")
                return True
        return False
    #unique validation
    user_fields = {
        "phone": data.get("phone"),
        "email": data.get("email"), 
    }

    if check_unique(User, user_fields, "User"):
        return redirect_with_context()

    # Check Company uniqueness
    company_fields = {"name": data.get("name")}
    optional_fields = ["website", "contact_person_email"]
    for field in optional_fields:
        if data.get(field):
            company_fields[field] = data.get(field)

    if check_unique(Company, company_fields, "Company"):
        return redirect_with_context()

    return None  # Everything is valid


@permission_required('register_company')
def register_company(request):
    if request.method == "POST":
        password = None
        data = {key: (value.strip() if value.strip() != '' else None) for key, value in request.POST.items()}
        # Start a transaction block to ensure all operations succeed or fail together
        # data = request.POST
        validation_response = validate_company_data(request, data)
        if validation_response:  # If validation returned a response (i.e., an error), stop execution
            return validation_response  # Directly return from here    
        
        logo = request.FILES.get("logo") 
        password  = generate_random_password()
        # print(password)
        #firstly user creation
        try:
            with transaction.atomic():

                user = User(
                    email = data.get("email"),
                    password = make_password(password),
                    phone = data.get("phone")
                )
                user.save()

                #after than company creation 
                city = City.objects.get(id=data.get("headquater"))

                industry_id = data.get("industry")
                industry = Industry.objects.get(id=industry_id) if industry_id else None

                position_id = data.get("contact_person_position")
                position = JobPosition.objects.get(id=position_id) if position_id else None

                # if logo and logo.size>0:
                #     print("logo not detected")
                company = Company(
                    id=user,
                    name=data.get("name"),
                    website=data.get("website", "") or None,
                    founded_year=data.get("founded_year","") or None,
                    category=data.get("category"),
                    industry=industry,
                    headquater=city,
                    contact_person_name=data.get("contact_person_name", "") or None,
                    contact_person_email=data.get("contact_person_email", "") or None,
                    contact_person_position=position,
                    address=data.get("address", "") or None,
                    description= data.get("description","") or None,
                    logo= logo,  # Save uploaded file
                )

                if data.get("company_size"):
                    company.company_size = data.get("company_size")

                if data.get("company_type"):
                    company.company_type = data.get("company_type")

                company.save()
                role = Role.objects.filter(name='Company').first()
                if not role:
                    messages.error(request,"Role 'Company' does not exist.")
                    return redirect("list_companies")
                                
                user_role = UserRole(user = user,role = role)
                user_role.save()
                send_registration_email(user.email,password)
                # Success message
                messages.success(request, f"Company {company.name} registered successfully.")
                return redirect("list_companies")
            
        except ValidationError as e:
            context = get_company_registration_context()
            for field, error_list in e.message_dict.items():
                for err in error_list:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
            return render(request, "company_registration.html", context)

        except Exception as e:
            context = get_company_registration_context()
            messages.error(request, "An unexpected error occurred. Please try again.")
            # return ResponseModel({},str(e),500)
            return render(request, "company_registration.html", context)

    context = get_company_registration_context()
    messages.error(request,"Invalid request method passed")
    return render(request,"company_registration.html", context)

@permission_required('edit_company')
def edit_company_page(request,id=0):
    url = reverse('view_company', kwargs={'id': id}) + "?mode=edit"
    return redirect(url)
    # return ResponseModel(data,"Dropdowns Get Succesfully",200)

@permission_required('view_company','edit_company')
def view_company(request,id=0):
    company = get_object_or_404(Company,id=id)
    user = company.id
    user_payload = get_user_from_jwt(request)
    user_role = user_payload.get("role") if user_payload else None
    edit_company = has_permission(user_role, 'edit_company')
    mode = request.GET.get('mode', 'view')
    
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
            "country": safe_deep_get(company.headquater, "state.country.name"),
            "state_id": safe_deep_get(company.headquater, "state.id"),
            "country_id":safe_deep_get(company.headquater,"state.country.id")
        } ,
        "permissions":{
            "edit_company" : edit_company
        },
        "description":company.description,
        "contact_person_name" : company.contact_person_name ,
        "contact_person_email" : company.contact_person_email,
        "contact_person_position" : {
            "value": safe_value(company.contact_person_position, "id"),
            "display": safe_value(company.contact_person_position, "name"),
        } ,
        "address" : company.address,
        "created_at" : company.created_at,
        "logo" : company.logo if company.logo else None
    } 
    
    if(mode == 'edit'):
        context = get_company_registration_context()
        data.update(context)
        data['header_title']= "Edit Company"
        data['header_subtitle']= "Edit registered company details"
        data['button'] = "Edit Company"
        
        return render(request,'company_registration.html',data)
    
    print('here',data['id'])
    return render(request,'view_company.html',data)


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
        
        # Check if the user has the 'add_students' and 'delete_students' permissions
        user_payload = get_user_from_jwt(request)
        user_role = user_payload.get("role") if user_payload else None
        add_company = has_permission(user_role, 'register_company')
        view_company = has_permission(user_role, 'view_company')
        delete_company = has_permission(user_role, 'delete_company')
        # response={
        #     "data":result,
        #     "total":total,
        #     "pagination":pagination
        # } 
        return render(request, "companies_list.html", {
            "data": result,
            "total": total,
            "pagination": pagination,
            "filter_options": filter_options,
            "permissions":{
                "add_company" : add_company,
                "view_company" : view_company,
                "delete_company" : delete_company
            }
        })
    
    messages.error(request,"Invalid request method")
    return redirect("dashboard")


@permission_required('edit_company')
def edit_company(request,id=0):
    if request.method == "POST":
        try:
            company = Company.objects.get(id=id)
            data = {key: (value.strip() if value.strip() != '' else None) for key, value in request.POST.items()}
            validation_response = validate_company_data(request, data,True,id)
            if validation_response:  # If validation returned a response (i.e., an error), stop execution
                return validation_response  # Directly return from here   
             
            # Update fields
            company.name = data.get("name", company.name)
            company.website = data.get("website", company.website)
            company.founded_year=data.get("founded_year",company.founded_year)
            company.category = data.get("category",company.category)
            company.id.email = data.get("email", company.id.email)
            company.id.phone = data.get("phone", company.id.phone)
            company.company_size = data.get("company_size", company.company_size)
            company.company_type = data.get("company_type", company.company_type)
            company.contact_person_name = data.get("contact_person_name", company.contact_person_name)
            company.contact_person_email = data.get("contact_person_email", company.contact_person_email)
            company.address = data.get("address", company.address)
            company.description=data.get("description",company.description)

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

            
            messages.success(request, f"Company {company.name} updated successfully.")
            return redirect("list_companies")
        
        except Company.DoesNotExist:
            messages.error(request, "Company not found")
            return redirect("list_companies")
        
        except ValidationError as e:
            # context = get_company_registration_context()
            for field, error_list in e.message_dict.items():
                for err in error_list:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
            return redirect("edit_company_page",id=id)

        except Exception as e:
            print("ste",str(e))
            messages.error(request,"An Unexpected Error Ocuured, Please try again")
            return redirect("edit_company_page",id=id)
        
    messages.error(request, "Invalid Request Method Found")
    return redirect("list_companies")

@permission_required('delete_company')
def delete_company(request):
    if request.method == "POST":
        company_id = request.POST.get("company_id")
        if not company_id:
            messages.error(request, "company id is required to delete.")
            return redirect("list_companies")
        try:
            with transaction.atomic():
                company = Company.objects.get(id=company_id)
                # company = get_object_or_404(Company, id=company_id)
                user = company.id

                # Check for assigned jobs
                # if Job.objects.filter(company=company).exists():
                #     return ResponseModel({},"Cannot delete company with assigned jobs",400)
                
                # Check for company_drive mapping
                if CompanyDrive.objects.filter(company=company).exists():
                    messages.error(request,"Cannot delete company mapped in company_drive")
                    return redirect('list_companies')
                    # return ResponseModel({},"Cannot delete company mapped in company_drive",400)
                
                # Delete company 
                company.delete()
                user.delete()

                messages.success(request,"Company deleted successfully")
                return redirect('list_companies')
                # return ResponseModel({},"Company deleted successfully",200)
        except Company.DoesNotExist:
                messages.error(request,"Company not found")
                return redirect("list_companies")
        except Exception as e:
            messages.error(request,str(e))
            return redirect('list_companies')
            # return ResponseModel({},str(e),500)

    messages.error(request,"Invalid request method")
    return redirect('list_companies')
    # return render(request,'list_companies.html')
    # return ResponseModel({},"Invalid request method",400)

# def get_industries(request):
#     industries = list(Industry.objects.values("id", "name").order_by("name"))
#     return ResponseModel(industries,"Industries Fetch Succesfully",200)
    