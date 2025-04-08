from django.db import models
from .companies import Company
from .job_positions import JobPosition

# Job Type Choices
class JobType(models.TextChoices):
    FULL_TIME = 'Full-time', 'Full-time'
    PART_TIME = 'Part-time', 'Part-time'
    INTERNSHIP = 'Internship', 'Internship'
    CONTRACT = 'Contract', 'Contract'

# Job Mode Choices
class JobMode(models.TextChoices):
    OFFLINE = 'Offline', 'Offline'
    REMOTE = 'Remote', 'Remote'
    HYBRID = 'Hybrid', 'Hybrid'

class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    job_type = models.CharField(max_length=20,choices=JobType.choices)
    job_mode = models.CharField(max_length=20,choices=JobMode.choices)
    salary_package_min = models.DecimalField(max_digits=10,decimal_places=2)
    salary_package_max = models.DecimalField(max_digits=10,decimal_places=2)
    bond = models.CharField(max_length=100,blank=True,null=True)
    minimum_cgpa = models.FloatField(blank=True,null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    tenth = models.FloatField(null=True, blank=True)
    twelth = models.FloatField(null=True, blank=True)
    diploma = models.FloatField(null=True, blank=True)
    undergraduate = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'jobs'

    def __str__(self):
        return f"{self.job_title} - {self.get_job_status_display()}"
