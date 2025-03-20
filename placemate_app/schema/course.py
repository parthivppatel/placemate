from django.db import models
from .branch import Branch

class Course(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'courses'  # Set actual table name

    def __str__(self):
        return self.name
