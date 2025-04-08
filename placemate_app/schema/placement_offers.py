from django.db import models
from .students import Student
from .companies import Company
from .jobs import Job 
from .company_drives import CompanyDrive

# Status Choices
class OfferStatus(models.TextChoices):
    OFFERED = 'Offered', 'Offered'
    ACCEPTED = 'Accepted', 'Accepted'
    DECLINED = 'Declined', 'Declined'

class PlacementOffer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE) 
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    drive = models.ForeignKey(CompanyDrive,on_delete=models.RESTRICT, null=True, blank=True)
    offer_date = models.DateTimeField()
    package = models.FloatField()
    status = models.CharField(max_length=10,choices=OfferStatus.choices,default=OfferStatus.OFFERED)

    class Meta:
        db_table = 'placement_offers'
        unique_together = ('student', 'job','drive')

    def __str__(self):
        return f"Offer for {self.student.first_name} {self.student.last_name}"
