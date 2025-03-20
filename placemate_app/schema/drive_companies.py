from django.db import models
from .placement_drives import PlacementDrive
from .companies import Company

class DriveCompany(models.Model):
    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        db_table = 'drive_companies'
        unique_together = ('drive', 'company')

    def __str__(self):
        return f"{self.company.name} - {self.drive.title}"
