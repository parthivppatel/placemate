from django.db import models
from .states import State

class City(models.Model):
    cityname = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    class Meta:
        db_table = 'Cities'
        
    def __str__(self):
        return f"{self.cityname}, {self.state.statename}, {self.state.country.name}"
