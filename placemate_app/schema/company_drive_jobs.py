
from django.db import models
from .jobs import Job
from .company_drives import CompanyDrive


class CompanyDriveJobs(models.Model):
    company_drive = models.ForeignKey(CompanyDrive, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "company_drive_jobs"
        unique_together = ('company_drive', 'job')
    
    def __str__(self):
        return f"{self.company_drive.drive_name} - {self.job.id}" 

    