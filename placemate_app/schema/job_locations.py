from django.db import models
from .jobs import Job
from .cities import City

class JobLocation(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        db_table = 'job_locations'
        unique_together = ('job', 'city')

    def __str__(self):
        return f"{self.job.job_title} - {self.city.cityname}"
