from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'skills'

    def __str__(self):
        return self.name