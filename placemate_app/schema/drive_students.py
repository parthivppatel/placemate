from django.db import models
from .placement_drives import PlacementDrive
from .students import Student

class DriveStudent(models.Model):
    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        db_table = 'drive_students'
        unique_together = ('drive', 'student')

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.drive.title}"
