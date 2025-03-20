from django.db import models
from .jobs import Job
from .skills import Skill

class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = 'job_skills'
        unique_together = ('job', 'skill')

    def __str__(self):
        return f"{self.job.job_title} - {self.skill.name}"
