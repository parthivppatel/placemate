from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'branch'  # Set actual table name

    def __str__(self):
        return self.name
