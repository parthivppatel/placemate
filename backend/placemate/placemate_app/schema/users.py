from django.db import models

class User(models.Model):
    class Meta:
        db_table = 'User'
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.email