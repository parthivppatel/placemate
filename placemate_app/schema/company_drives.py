from django.db import models
from ..schema import Company


class DriveStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    ONGOING = "ongoing", "Ongoing"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"

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

class CompanyDrive(models.Model):
    
    id = models.AutoField(primary_key=True)
    drive_name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=20,choices=JobType.choices)
    job_mode = models.CharField(max_length=20,choices=JobMode.choices)
    ug_package_min = models.FloatField(null=True, blank=True)
    ug_package_max = models.FloatField(null=True, blank=True)
    pg_package_min = models.FloatField(null=True, blank=True)
    pg_package_max = models.FloatField(null=True, blank=True)
    stipend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bond = models.CharField(max_length=100,blank=True,null=True)
    minimum_cgpa = models.FloatField(blank=True,null=True)
    tenth = models.FloatField(null=True, blank=True)
    twelth = models.FloatField(null=True, blank=True)
    diploma = models.FloatField(null=True, blank=True)
    undergraduate = models.FloatField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField() 
    status = models.CharField(
        max_length=10,
        choices=DriveStatus.choices,
        default=DriveStatus.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_drives'
    
    def __str__(self):
        return self.drive_name