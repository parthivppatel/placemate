from django.db import models
from .users import User
from .branch import Branch


class RoleEnum(models.TextChoices):
    HEAD = 'Head', 'Head'
    FACULTY_MEMBER = 'Faculty Member', 'Faculty Member'
    STUDENT_COORDINATOR = 'Student Coordinator', 'Student Coordinator'
    STUDENT_MEMBER = 'Student Member', 'Student Member'
    PLACEMENT_OFFICER = 'Placement Officer', 'Placement Officer'
    ASSISTANT_PLACEMENT_OFFICER = 'Assistant Placement Officer', 'Assistant Placement Officer'

class PlacementCellMember(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role_in_cell = models.CharField(max_length=30, choices=RoleEnum.choices, default=RoleEnum.STUDENT_MEMBER)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    join_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    active_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'placement_cell_members'  

    def __str__(self):
        return f"{self.id.email} - {self.role_in_cell}"
