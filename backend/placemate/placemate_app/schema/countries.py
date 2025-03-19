from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'Countries'
        
    def __str__(self):
        return self.name
