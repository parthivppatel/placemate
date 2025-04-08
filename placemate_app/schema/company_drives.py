from django.db import models
from ..schema import Company


class DriveStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    ONGOING = "ongoing", "Ongoing"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"

class CompanyDrive(models.Model):
    
    id = models.AutoField(primary_key=True)
    drive_name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField() 
    status = models.CharField(
        max_length=10,
        choices=DriveStatus.choices,
        default=DriveStatus.SCHEDULED
    )

    class Meta:
        db_table = 'comapany_drives'
    
    def __str__(self):
        return self.drive_name