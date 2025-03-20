from django.db import models
from .jobs import Job
from .course import Course

class JobCourses(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'job_courses'
        unique_together = ('job', 'course')

    def __str__(self):
        return f"{self.job.job_title} - {self.course.name}"
