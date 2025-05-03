from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError 
from ..schema.users import User
from ..schema.students import Student   
from ..schema.companies import Company
from ..schema.placement_cell_members import PlacementCellMember,RoleEnum
from ..schema.cities import City    
from ..schema.branch import Branch
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
from datetime import datetime
from decimal import Decimal, InvalidOperation

def get_member_context():
    return{
        "roles" : [{"value": role.value} for role in RoleEnum],
        "branches" : list(Branch.objects.values("id", "name"))
    }

 
@permission_required('add_member')
def member_registration_page(request):
    context = get_member_context()
    return render(request,'member_registration.html',context)

def validate_member_data(request,data,edit=False,id=0):
    def redirect_with_context():
        context = get_member_context()
        if edit:
            return redirect("edit_member_page", id=id)
        return render(request, "member_registration.html", context)
    
    # Validate required fields
    required_fields = ['email', 'phone', 'role','join_date']
 
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        messages.error(request,f"Missing required fields: {', '.join(missing_fields)}")
        return redirect_with_context() 
 
    role = data.get("role") 
    try:
        join_date = datetime.fromisoformat(data.get("join_date"))
        end_date_str = data.get("end_date")

        if end_date_str:
            end_date = datetime.fromisoformat(data.get("end_date"))
            if  join_date >= end_date: 
                messages.error(request,"Join date cannot be greater than equal to end date.")
                return redirect_with_context()
                
    except ValueError:
        messages.error(request,"Invalid datetime format. Use ISO format: YYYY-MM-DD.")
        return redirect_with_context()
    if role not in RoleEnum.values:
        messages.error(request,f"Invalid job_type: '{role}'. Must be one of {RoleEnum.values}")
        return redirect_with_context()

    return None
 
@permission_required('add_member')
def add_member(request):
    if request.method == "POST":
        password = None
        data = {key: (value.strip() if value.strip() != '' else None) for key, value in request.POST.items()}
        # Start a transaction block to ensure all operations succeed or fail together
        # data = request.POST
        validation_response = validate_member_data(request,data)
        if validation_response:  # If validation returned a response (i.e., an error), stop execution
            return validation_response  # Directly return from here    
 
        # print(password)
        #firstly user creation
        try:
            with transaction.atomic(): 
                user = User.objects.filter(email=data.get("email")).first()
                student = False
                if not user:   
                    password  = generate_random_password()
                    user = User(
                        email = data.get("email"),
                        password = make_password(password),
                        phone = data.get("phone")
                    )
                    user.save()
            
                else:
                    if Company.objects.filter(id= user.id).exists():
                        messages.error(request,"Cannot create admin with registered company id")
                        return render(request, "member_registration.html",get_member_context())
                
                    if Student.objects.filter(student_id=user.id).exists():
                        student = True

                        # Check if student already has a role assigned
                        if UserRole.objects.filter(user=user,role_id=3).exists():
                            messages.error(request, "Student is already assigned a role.")
                            return render(request, "member_registration.html", get_member_context())
                    else:   
                        messages.error(request,"Email Id already registered")
                        return render(request, "member_registration.html",get_member_context())

                branch = Branch.objects.filter(id = data.get("branch")).first()

                member = PlacementCellMember(
                    id=user,
                    role_in_cell = data.get("role"),
                    branch = branch,
                    join_date = data.get("join_date"),
                    end_date = data.get("end_date"),
                    description= data.get("description","") or None
                )

                member.save()

                role = Role.objects.filter(name='Admin').first()
                if not role:
                    messages.error(request,"Role 'Admin' does not exist.")
                    return redirect("list_members")
                                
                user_role = UserRole(user = user,role = role)
                user_role.save()

                if not student: 
                    send_registration_email(user.email,password)
                # Success message
                messages.success(request, f"Placement member registered successfully.")
                return redirect("list_members")
            
        except ValidationError as e:
            context = get_member_context()
            for field, error_list in e.message_dict.items():
                for err in error_list:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
            return render(request, "member_registration.html", context)

        except Exception as e:
            context = get_member_context() 
            messages.error(request, "An unexpected error occurred. Please try again.")
            # return ResponseModel({},str(e),500)
            return render(request, "member_registration.html", context)

    context = get_member_context()
    messages.error(request,"Invalid request method passed")
    return render(request,"member_registration.html", context)

@permission_required('edit_member')
def edit_member_page(request,id=0):
    url = reverse('view_member', kwargs={'id': id}) + "?mode=edit"
    return redirect(url)
    # return ResponseModel(data,"Dropdowns Get Succesfully",200)

@permission_required('view_member','edit_member')
def view_member(request,id=0):
    member = get_object_or_404(PlacementCellMember,id=id)
    mode = request.GET.get('mode', 'view')
 
 
    # Check if the user has the 'add_students' and 'delete_students' permissions
    user_payload = get_user_from_jwt(request)
    user_role = user_payload.get("role") if user_payload else None
    edit_member = has_permission(user_role, 'edit_member')
    student = Student.objects.filter(student_id=member.id.id).first()

    data={
        "id":member.id.id,
        "name": (student.first_name + " " + student.last_name) if student else "Placement Member",
        "email" : member.id.email,
        "phone":member.id.phone,
        "branch": member.branch.name if member.branch else None,
        "join_date" : member.join_date,
        "end_date" : member.end_date,
        "description" : member.description,
        "role" :member.role_in_cell,
        "profile" : student.profile if student and student.profile else None,
        "active_status" : member.active_status,
        "edit_member":edit_member
    } 

    if(mode == 'edit'): 
        data.update(get_member_context()) 
        return render(request,'edit_member.html',data)
    
    return render(request,'view_member.html',data)


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

@permission_required('view_members')  
def list_members(request):
    # page,perpage = 1,10
    if request.method == "GET":
        data = request.GET
        # filters = data.get("filters", {})
        sort = data.get("sort", {})
        validate_pg = validate_pagination(data)
        if validate_pg is None:
            messages.error(request,"page and perpage must be valid positive integers")
            return redirect('dashboard')
        page, perpage = validate_pg

        # data gathering
        members = PlacementCellMember.objects.filter(active_status = True)

        # companies = companies.annotate(
        #     company_type_label=Case
        #     (
        #         *[When(company_type=value, then=Value(label)) for value, label in CompanyType.choices],
        #         output_field=CharField()
        #     )
        # )

        # filtering
        if search := data.get("search","").strip():
            members = members.filter(id__email__icontains=search)
        
        if role_in_cell:= data.get("role","").strip():
            members = members.filter(role_in_cell=role_in_cell)

        #sorting
        sort_field = sort.get("field", "").strip()  # Clean up any accidental whitespace
        sort_type = sort.get("type", "asc").lower()
        
        ordering = "-join_date"
        if sort_field :
            if sort_field == "email":
                ordering = "id__email"
            elif sort_field == "role":
                ordering = "role" 
            elif sort_field == "end_date":
                ordering = "end_date"
            # elif sort_field == "company_type":
            #     ordering = "company_type_label"
            else:
                ordering= "join_date"

            if sort_type == "desc":
                ordering = f"-{ordering}"

        members = members.order_by(ordering)

        #pagination
        members, total, pagination = paginate(members, page, perpage)

        result = []
        for member in members:
            result.append({
                "id": member.id.id,
                "email": member.id.email,
                "join_date": member.join_date,
                "end_date": member.end_date,
                "role": member.role_in_cell
            })

        filter_options={      
            "roles": [
                {"value": role.value} for role in RoleEnum
            ]
         }
         
        user_payload = get_user_from_jwt(request)
        user_role = user_payload.get("role") if user_payload else None
        add_member = has_permission(user_role, 'add_member')
        view_member = has_permission(user_role, 'view_member')
        delete_member = has_permission(user_role, 'delete_member')
        # response={
        #     "data":result,
        #     "total":total,
        #     "pagination":pagination
        # } 
        
        return render(request, "members_list.html", {
            "data": result,
            "total": total,
            "pagination": pagination,
            "filter_options": filter_options,
            "permissions":{
                "add_member" : add_member,
                "view_member" : view_member,
                "delete_member" : delete_member
            }
        })
    
    messages.error(request,"Invalid request method")
    return redirect("dashboard")


@permission_required('edit_member')
def edit_member(request,id=0):
    if request.method == "POST":
        try: 
            member = PlacementCellMember.objects.get(id=id)
            data = {key: (value.strip() if value.strip() != '' else None) for key, value in request.POST.items()}
            validation_response = validate_member_data(request, data,True,id)
            if validation_response:  # If validation returned a response (i.e., an error), stop execution
                return validation_response  # Directly return from here   
             
            # Update fields
            member.id.phone = data.get("phone", member.id.phone)
            member.role_in_cell = data.get("role", member.role_in_cell)
            member.join_date = data.get("join_date",member.join_date)
            member.end_date = data.get("end_date", member.end_date) 
            member.description=data.get("description",member.description)

            branh_id = data.get("branch")
            if branh_id:
                member.branch = Branch.objects.get(id=branh_id)

            member.id.save()
            member.save()
 
            messages.success(request, f"placement Member updated successfully.")
            return redirect("list_members")
        
        except PlacementCellMember.DoesNotExist:
            messages.error(request, "Member not found")
            return redirect("list_members")
        
        except ValidationError as e:
            # context = get_company_registration_context()
            for field, error_list in e.message_dict.items():
                for err in error_list:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
            return redirect("edit_company_page",id=id)

        except Exception as e:
            print("ste",str(e))
            messages.error(request,"An Unexpected Error Ocuured, Please try again")
            return redirect("edit_member_page",id=id)
        
    messages.error(request, "Invalid Request Method Found")
    return redirect("list_companies")

@permission_required('delete_member')
def delete_member(request):
    if request.method == "POST":
        member_id = request.POST.get("member_id")
        if not member_id:
            messages.error(request, "placement cell member id is required to delete.")
            return redirect("list_members")
        try:
            with transaction.atomic():
                member = PlacementCellMember.objects.get(id=member_id) 
                user = member.id

                member.delete()
                # Check for company_drive mapping
                if Student.objects.filter(student_id=user.id).exists(): 
                    UserRole.objects.filter(user=user,role_id = 3).delete()
                else:  
                    user.delete()

                messages.success(request,"Placement cell Member deleted successfully")
                return redirect('list_members')
        except PlacementCellMember.DoesNotExist:
                messages.error(request,"Placement cell member not found")
                return redirect("list_members")
        except Exception as e:
            messages.error(request,str(e))
            return redirect('list_members') 

    messages.error(request,"Invalid request method")
    return redirect('list_members') 
 