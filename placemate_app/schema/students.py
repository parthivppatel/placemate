from django.db import models
from .users import User
from .companies import Company
from .cities import City
from .course import Course

# Gender Choices
class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'

# Placement Status Choices
class PlacementStatus(models.IntegerChoices):
    NOT_PLACED = 0, 'Not Placed'
    PLACED = 1, 'Placed'
    INTERN = 2, 'Internship'
    JOB_OFFER = 3, 'Job Offer Received'

class GraduationStatus(models.TextChoices):
    PURSUING = 'Pursuing', 'Pursuing'
    COMPLETED = 'Completed', 'Completed'
    DROPPED_OUT = 'Dropped Out', 'Dropped Out'

class Student(models.Model):
    student_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    enrollment = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        null=True
    )
    joining_year = models.PositiveIntegerField()
    cgpa = models.FloatField(null=True, blank=True)
    profile = models.CharField(max_length=255, blank=True, null=True)
    placement_status = models.PositiveSmallIntegerField(
        choices=PlacementStatus.choices,
        default=PlacementStatus.NOT_PLACED
    )
    graduation_status = models.CharField(
        max_length=20,
        choices=GraduationStatus.choices,
        default=GraduationStatus.PURSUING
    )
    company_placedIn = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="placed_students")
    package = models.FloatField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    tenth_percentage = models.FloatField(null=True, blank=True)  # New field for 10th percentage
    twelfth_percentage = models.FloatField(null=True, blank=True)  # New field for 12th percentage
    backlog = models.PositiveIntegerField(default=0)  # New field for backlog count
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.enrollment})"
