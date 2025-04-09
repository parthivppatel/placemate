from django.db import models
from .company_drives import CompanyDrive
from .course import Course

class DriveCourses(models.Model):
    drive = models.ForeignKey(CompanyDrive, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'drive_courses'
        unique_together = ('drive', 'course')

    def __str__(self):
        return f"{self.drive.drive_name} - {self.course.name}"
