from django.db import models
from .countries import Country

class State(models.Model):
    statename = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    class Meta:
        db_table = 'States'
        
    def __str__(self):
        return f"{self.statename}, {self.country.name}"
