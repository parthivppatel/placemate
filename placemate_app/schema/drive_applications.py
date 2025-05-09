from django.db import models 
from .students import Student
from .company_drives import CompanyDrive
# Status Choices
class ApplicationStatus(models.TextChoices):
    APPLIED = 'Applied', 'Applied'
    REVIEWED = 'Reviewed', 'Reviewed'
    SHORTLISTED = 'Shortlisted', 'Shortlisted'
    REJECTED = 'Rejected', 'Rejected'
    SELECTED = 'Selected', 'Selected'

class DriveApplication(models.Model): 
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    drive = models.ForeignKey(CompanyDrive,on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20,choices=ApplicationStatus.choices,default=ApplicationStatus.APPLIED)
    resume_link = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'drive_applications'

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.get_status_display()}"
