from django.db import models

class Role(models.Model):
    class Meta:
        db_table = 'Roles'
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name
