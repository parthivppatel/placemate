from django.db import models
from .company_drives import CompanyDrive
from .skills import Skill

class DriveSkill(models.Model):
    drive = models.ForeignKey(CompanyDrive, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = 'drive_skills'
        unique_together = ('drive', 'skill')

    def __str__(self):
        return f"{self.drive.drive_name} - {self.skill.name}"
