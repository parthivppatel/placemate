from django.db import models
from .drive_applications import DriveApplication

# Interview Type Choices
class InterviewType(models.TextChoices):
    HR = 'HR', 'HR'
    TECHNICAL = 'Technical', 'Technical' 
    GROUP_DISCUSSION = 'Group Discussion', 'Group Discussion'
    APTITUDE_TEST = 'Aptitude Test', 'Aptitude Test'

# Interview Mode Choices
class InterviewMode(models.TextChoices):
    ONLINE = 'Online', 'Online'
    OFFLINE = 'Offline', 'Offline'

# Interview Status Choices
class InterviewStatus(models.TextChoices):
    SCHEDULED = 'Scheduled', 'Scheduled'
    COMPLETED = 'Completed', 'Completed'
    CANCELLED = 'Cancelled', 'Cancelled'

# Interview Result Choices
class InterviewResult(models.TextChoices):
    PASSED = 'Passed', 'Passed'
    FAILED = 'Failed', 'Failed'
    ON_HOLD = 'On-Hold', 'On-Hold'

class Interview(models.Model):
    application = models.ForeignKey(DriveApplication, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    interview_type = models.CharField(max_length=20,choices=InterviewType.choices)
    mode = models.CharField(max_length=10,choices=InterviewMode.choices)
    status = models.CharField(max_length=15,choices=InterviewStatus.choices,default=InterviewStatus.SCHEDULED)
    result = models.CharField(max_length=10,choices=InterviewResult.choices,null=True,blank=True)
    interview_date = models.DateTimeField()

    class Meta:
        db_table = 'interviews'

    def __str__(self):
        return f"Round {self.round_number} - {self.application.student.first_name} - {self.get_interview_type_display()} - {self.get_status_display()}"
