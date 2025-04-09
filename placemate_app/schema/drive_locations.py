from django.db import models
from .company_drives import CompanyDrive
from .cities import City

class DriveLocation(models.Model):
    drive = models.ForeignKey(CompanyDrive, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        db_table = 'drive_locations'
        unique_together = ('drive', 'city')

    def __str__(self):
        return f"{self.drive.drive_name} - {self.city.cityname}"
