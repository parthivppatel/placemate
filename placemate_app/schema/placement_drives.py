from django.db import models

# Status Choices
class DriveStatus(models.TextChoices):
    ONGOING = 'Ongoing', 'Ongoing'
    COMPLETED = 'Completed', 'Completed'

class PlacementDrive(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    drive_from = models.DateTimeField()
    drive_to = models.DateTimeField()
    status = models.CharField(max_length=15,choices=DriveStatus.choices,default=DriveStatus.ONGOING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'placement_drives'

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
