from django.shortcuts import render, get_object_or_404
from ...schema.companies import Company

def company_profile(request):
    # Assuming the logged-in user is linked to the company
    company = get_object_or_404(Company, id=request.user.id)
    return render(request, 'Company/company_profile.html', {'company': company})