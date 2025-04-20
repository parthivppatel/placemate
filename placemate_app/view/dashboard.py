from datetime import timezone
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count,Q,Case, When, IntegerField,CharField, Value,F

from django.shortcuts import render
from ..decorators import permission_required
from ..utils.jwt_utils import get_user_from_jwt 

from collections import Counter

from ..schema.students import Student  
from ..schema.users import User  
from ..schema.course import Course
from ..schema.companies import Company
from ..schema.drive_applications import DriveApplication
from ..schema.company_drives import CompanyDrive
from ..schema.placement_offers import PlacementOffer, OfferStatus
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


def get_students_details(student):
    application_status = DriveApplication.objects.filter(student=student).values_list('status', flat=True)
    status_counts = Counter(application_status)

    status_data = {
        'Applied': status_counts.get('Applied', 0),
        'Shortlisted': status_counts.get('Shortlisted', 0),
        'Interview': status_counts.get('Interview', 0),
        'Offered': status_counts.get('Offered', 0),
        'Rejected': status_counts.get('Rejected', 0),
    }

    today = timezone.now()
    four_months_ago = today - timezone.timedelta(days=120)

    drive_data = (
        DriveApplication.objects
        .filter(student=student, created_at__gte=four_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    month_map = {entry['month'].strftime('%b'): entry['count'] for entry in drive_data}

    drive_labels = []
    drive_counts = []

    for i in range(3, -1, -1):
        month = (today - timezone.timedelta(days=30 * i)).strftime('%b')
        drive_labels.append(month)
        drive_counts.append(month_map.get(month, 0))

    eligible_drives = CompanyDrive.objects.filter(end_date__gte=today) 
    eligible_drives_data = []

    for drive in eligible_drives:
        eligible = True
        
        if drive.minimum_cgpa and (student.cgpa or 0) < drive.minimum_cgpa:
            eligible = False
        if drive.tenth and (student.tenth_percentage or 0) < drive.tenth:
            eligible = False
        if drive.twelth and (student.twelfth_percentage or 0) < drive.twelth:
            eligible = False
        
        if eligible:
            eligible_drives_data.append({
                'id': drive.id,
                'company': drive.company.name,
                'role': drive.drive_name, 
                'package': f"{drive.ug_package_min} - {drive.ug_package_max}",  
                'end_date': drive.end_date.strftime('%Y-%m-%d'), 
            })

    student_applications = DriveApplication.objects.filter(student=student)
    application_data = []

    for application in student_applications:
        application_data.append({
            'company': application.drive.company.name,  
            'drive': application.drive.drive_name,
            'applied_on': application.created_at.strftime('%Y-%m-%d'),
            'status': application.get_status_display(),  
        })

    try:
        accepted_offer = PlacementOffer.objects.get(student=student, status=OfferStatus.ACCEPTED)
        if accepted_offer.job and accepted_offer.job.drive and accepted_offer.job.drive.company:
            offer_data = {
                "company": accepted_offer.job.drive.company.name,
                "role": accepted_offer.job.job_title,
                "package": f"{accepted_offer.package} LPA",
                "status": accepted_offer.status,
                "offer_date": accepted_offer.offer_date.strftime('%Y-%m-%d'),
            }
        else:
            offer_data = None
    except PlacementOffer.DoesNotExist:
        offer_data = None

    return {
        "status_data": status_data,
        "drive_chart": {
            "labels": drive_labels,
            "data": drive_counts
        },
        "eligible_drives": eligible_drives_data,
        "applications": application_data,
        "offers": offer_data
    }

def get_sumary_details():
    today = datetime.now()
    start_of_year = datetime(timezone.now().year, 1, 1)
    end_of_year = datetime(timezone.now().year, 12, 31)

    placed_students_count = PlacementOffer.objects.filter(offer_date__range=(start_of_year, end_of_year)).values('student_id').distinct().count()
    visited_companies_count = CompanyDrive.objects.filter(created_at__range=(start_of_year, end_of_year)).values('company_id').distinct().count()
    total_drives_count = CompanyDrive.objects.filter(start_date__range=(start_of_year, end_of_year)).count()
    total_applications_count = DriveApplication.objects.filter(created_at__range=(start_of_year, end_of_year)).count()


    months_data = []
    for i in range(5, -1, -1):
        month = today - relativedelta(months=i)
        label = month.strftime("%b '%y")
        start = datetime(month.year, month.month, 1)
        end = (start + relativedelta(months=1)) - timedelta(seconds=1)
    
        count = PlacementOffer.objects.filter(offer_date__range=(start, end)).values('student_id').distinct().count()
        months_data.append({'label': label, 'count': count})

    # Course-wise placement distribution (for this year)
    course_wise_distribution = Course.objects.annotate(
        count=Count(
            'student__placementoffer',
            filter=Q(student__placementoffer__offer_date__range=(start_of_year, end_of_year)),
            distinct=True
        )
    ).values('name', 'count').order_by('name')

    course_labels = [item['name'] for item in course_wise_distribution]
    course_counts = [item['count'] for item in course_wise_distribution]
    
    # Get upcoming drives with the count of applications (limited to 4)
    upcoming_drives = CompanyDrive.objects.filter(
        start_date__gte=timezone.now()  # Drives starting in the future
    ).order_by('start_date')[:4].values(
        'id',
        'drive_name',
        'start_date',
        'status',
        'company__logo',
        'company__name',
        # Include the application count in the result
    )

    upcoming_drives_list = [{
    'id' : drive['id'],
    'drive_name': drive['drive_name'],
    'start_date': drive['start_date'].strftime('%b %d, %Y'),
    'company_name': drive['company__name'],
    'status': drive['status'], 
    'logo': drive['company__logo'] 
    } for drive in upcoming_drives]

 
    # Query the DriveApplication model and group by salary ranges
    salary_counts = PlacementOffer.objects.filter(
        offer_date__range=(start_of_year, end_of_year),
        package__isnull=False
    ).annotate(
        salary_range=Case(
            When(package__gte=3, package__lte=5, then=Value("3-5 LPA")),
            When(package__gte=5, package__lte=8, then=Value("5-8 LPA")),
            When(package__gte=8, package__lte=12, then=Value("8-12 LPA")),
            When(package__gte=12, package__lte=18, then=Value("12-18 LPA")),
            When(package__gte=18, package__lte=25, then=Value("18-25 LPA")),
            When(package__gte=25, then=Value("25+ LPA")),
            output_field=CharField()
        )
    ).values('salary_range').annotate(student_count=Count('id')).order_by('salary_range') 

    # Extract the counts for each salary range
    salary_data = {
        "3-5 LPA": 0,
        "5-8 LPA": 0,
        "8-12 LPA": 0,
        "12-18 LPA": 0,
        "18-25 LPA": 0,
        "25+ LPA": 0,
    }

    # Populate the salary_data dictionary with the counts
    for entry in salary_counts:
        salary_data[entry['salary_range']] = entry['student_count']

    # Prepare the data to be sent to the frontend
    salary_ranges_data = [
        salary_data["3-5 LPA"],
        salary_data["5-8 LPA"],
        salary_data["8-12 LPA"],
        salary_data["12-18 LPA"],
        salary_data["18-25 LPA"],
        salary_data["25+ LPA"],
    ]

    # Total students per branch
    total_students_per_branch = Student.objects.values(branch_id=F('course__branch_id'),branch_name=F('course__branch__name') ).annotate(total=Count('student_id'))

    # Placed students per branch (distinct student_id from PlacementOffer)
    placed_students_per_branch = PlacementOffer.objects.filter(offer_date__range=(start_of_year, end_of_year))\
    .values(branch_id=F('student__course__branch_id'),branch_name=F('student__course__branch__name')
    ).annotate(placed=Count('student_id', distinct=True))

    # Merge and calculate percentages
    branch_performance = []
    placed_dict = {item['branch_id']: item for item in placed_students_per_branch}

    for item in total_students_per_branch:
        branch_id = item['branch_id']
        placed_count = placed_dict.get(branch_id, {}).get('placed', 0)
        percentage = round((placed_count / item['total']) * 100) if item['total'] else 0

        branch_performance.append({
            'branch': item['branch_name'],
            'percentage': percentage,
            'placed': placed_count,
            'total': item['total']
        })

    return {
        'today':today,
        'card': {
            'visited':visited_companies_count,
            'drives': total_drives_count,
            'applications': total_applications_count,
            'placed' : placed_students_count
        },
        'placement_trend': months_data,
        'placement_distribution':{
            'labels': course_labels,
            'data': course_counts
        },
        'upcoming_drives':upcoming_drives_list,
        'salary_range': salary_ranges_data,
        'branch_performance':branch_performance
    }

@permission_required('view_dashboard')
def dashboard(request):
    # Extract user data from the token
    user_payload = get_user_from_jwt(request)
    if not user_payload:
        return render(request, "error.html", {"error": "Invalid or missing token"})

    user_email = user_payload.get("email")
    user_role = user_payload.get("role")
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return render(request, "403.html", {"error": "User not found"})

    if user_role == "Student":
        try:
            student = Student.objects.get(student_id=user)
        except Student.DoesNotExist:
            return render(request, "403.html", {"error": "Student not found"})

        student_dashboard_details = get_students_details(student)
        page_title = "Welcome, John Doe 👋"
        page_subtitle = "Here's a quick overview of your placement progress"
        return render(request, "student_dashboard.html", {
            "page_title": page_title,
            "page_subtitle": page_subtitle,
            "user_email": user_email,
            "student": student,  
            "profile_name": f"{student.first_name} {student.last_name}",
            "student_dashboard_details": student_dashboard_details,
        })

    elif user_role == "Company":
        return render(request, "company_dashboard.html", {"user_email": user_email})
    elif user_role == "Admin":
        admin_dashboard_details = get_sumary_details()

        return render(request, "admin_dashboard.html", {
            "data":admin_dashboard_details,
            "user_email": user_email
            })
    else:
        return render(request, "error.html", {"error": "Invalid role"})
