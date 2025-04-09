from django.db import models
from .users import User
from .industry import Industry
from .cities import City
from .job_positions import JobPosition

class CompanySize(models.IntegerChoices):
    MICRO = 0, "1-10 employees"
    SMALL = 1, "11-50 employees"
    MEDIUM = 2, "51-250 employees"
    LARGE = 3, "251-1000 employees"
    ENTERPRISE = 4, "1001+ employees"

class CompanyType(models.IntegerChoices):
    PRIVATE_LIMITED = 0, "Private Limited Company"
    PUBLIC_LIMITED = 1, "Public Limited Company"
    GOVERNMENT = 2, "Government Organization"
    NGO = 3, "Non-Profit Organization"
    STARTUP = 4, "Startup" 
    COOPERATIVE = 5, "Cooperative"
    MNC = 6, "Multinational Corporation"
    EDUCATIONAL = 7, "Educational Institution"
    
class Category(models.TextChoices):
    A = "A", "A"
    A1 = "A1", "A1"

class Company(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    website = models.URLField(max_length=255, blank=True, null=True,unique=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.A
    )
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    company_size = models.PositiveSmallIntegerField(
        choices=CompanySize.choices,
        default=CompanySize.SMALL
    )
    company_type = models.PositiveSmallIntegerField(
        choices=CompanyType.choices,
        default=CompanyType.PRIVATE_LIMITED
    )
    headquater = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_email = models.EmailField(max_length=255, blank=True, null=True,unique=True)
    contact_person_position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    # logo = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'companies'

    def __str__(self):
        return f"{self.name} - {self.status}"
