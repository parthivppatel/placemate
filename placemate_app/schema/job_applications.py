from django.db import models
from .jobs import Job
from .students import Student

# Status Choices
class ApplicationStatus(models.TextChoices):
    APPLIED = 'Applied', 'Applied'
    REVIEWED = 'Reviewed', 'Reviewed'
    SHORTLISTED = 'Shortlisted', 'Shortlisted'
    REJECTED = 'Rejected', 'Rejected'
    SELECTED = 'Selected', 'Selected'

class JobApplication(models.Model): 
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,choices=ApplicationStatus.choices,default=ApplicationStatus.APPLIED)
    resume_link = models.CharField(max_length=500)

    class Meta:
        db_table = 'job_applications'

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.job.job_title} - {self.get_status_display()}"
