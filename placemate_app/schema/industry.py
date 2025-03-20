from django.db import models

class Industry(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'industry'

    def __str__(self):
        return self.name
