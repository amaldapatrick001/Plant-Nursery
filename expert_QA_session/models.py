from django.db import models
from userauths.models import User_Reg, Expert
from django.utils import timezone

# Create your models here.

class ExpertSession(models.Model):
    SESSION_TYPES = [
        ('chat', 'Chat Session'),
        ('phone', 'Phone Call'),
        ('video', 'Video Call')
    ]

    session_id = models.AutoField(primary_key=True)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    user = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES)
    session_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.user.first_name} - {self.expert.user.first_name} ({self.session_type})"

    @property
    def is_past(self):
        return self.session_date < timezone.now()

    @property
    def can_be_cancelled(self):
        return not self.is_past


class ChatMessage(models.Model):
    sender = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User_Reg, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}"
