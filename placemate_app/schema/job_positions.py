from django.db import models

class JobPosition(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'job_positions'

    def __str__(self):
        return self.name
