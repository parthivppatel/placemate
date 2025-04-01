from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from ..schema.companies import  Company
from ..schema.users import User
from ..schema.industry import Industry
from ..schema.cities import City
from ..schema.job_positions import JobPosition
from ..utils import generate_random_password
from ..decorators import permission_required
from django.contrib.auth.hashers import make_password

@permission_required('register_company')
def register_company(request):
    if request.method == "POST":
        user = None
        try:
            data = request.POST
            logo = request.FILES.get("logo") 
            password  = generate_random_password()
            print(password)
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

            return JsonResponse({"message": "Company added successfully!"}, status=201)
        except ValidationError as e:
            if user:
                user.delete()
            return JsonResponse({"error": e.message_dict}, status=400)
        
        except Exception as e:
            if user:
                user.delete()
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "Invalid request method"}, status=405)
