from django.db import models
from .users import User

# Notification Types
class NotificationType(models.TextChoices):
    INFO = 'info', 'Info'
    SUCCESS = 'success', 'Success'
    WARNING = 'warning', 'Warning'
    ALERT = 'alert', 'Alert'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=10,choices=NotificationType.choices,default=NotificationType.INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.title} ({self.type})"
        return f"Broadcast - {self.title} ({self.type})"
