
from django.db import models
from .company_drives import CompanyDrive


class CompanyDriveJobs(models.Model):
    company_drive = models.ForeignKey(CompanyDrive, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    # job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "company_drive_jobs"
        # unique_together = ('company_drive', 'job')
    
    def __str__(self):
        return f"{self.company_drive.drive_name} - {self.job.id}" 

    