from django.db import models
from .users import User
from .branch import Branch

class DesignationEnum(models.TextChoices):
    PLACEMENT_OFFICER = "Placement Officer", "Placement Officer"
    ASSISTANT_PLACEMENT_OFFICER = "Assistant Placement Officer", "Assistant Placement Officer"

class Authority(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(
        max_length=30,
        choices=DesignationEnum.choices,
        default=DesignationEnum.ASSISTANT_PLACEMENT_OFFICER
    )
    qualification = models.CharField(max_length=255)
    profile = models.CharField(max_length=255)
    address = models.TextField()

    class Meta:
        db_table = 'authorities'

    def __str__(self):
        return f"{self.name} - {self.designation}"
