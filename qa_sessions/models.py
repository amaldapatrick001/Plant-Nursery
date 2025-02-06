from django.db import models
from django.utils.timezone import now
from userauths.models import Expert, User_Reg
import uuid
import datetime
from .utils import GoogleMeetService
from django.utils import timezone

class QnASession(models.Model):
    session_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, related_name="expert_sessions")
    customers = models.ManyToManyField(User_Reg, related_name="customer_sessions")
    max_participants = models.IntegerField(default=10)
    current_participants = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    google_meet_link = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='scheduled'
    )

    def __str__(self):
        return f"{self.title} - {self.expert.user.first_name}"

    def add_customer(self, customer):
        if self.current_participants < self.max_participants:
            self.customers.add(customer)
            self.current_participants += 1
            self.save()
            return True
        return False

    def generate_google_meet_link(self):
        """Generate a unique Google Meet link"""
        # Format: https://meet.google.com/xxx-xxxx-xxx
        unique_code = str(uuid.uuid4())[:12]  # Get first 12 characters of UUID
        formatted_code = f"{unique_code[:3]}-{unique_code[3:7]}-{unique_code[7:]}"
        return f"https://meet.google.com/{formatted_code}"

    def save(self, *args, **kwargs):
        if not self.google_meet_link:
            try:
                meet_service = GoogleMeetService()
                self.google_meet_link = meet_service.create_meeting(
                    title=self.title,
                    start_time=self.start_time,
                    end_time=self.end_time,
                    description=self.description
                )
            except Exception as e:
                print(f"Failed to create Google Meet link: {e}")
                # Fallback to a placeholder link if Google Meet creation fails
                self.google_meet_link = f"https://meet.google.com/placeholder-{uuid.uuid4().hex[:8]}"
        
        super().save(*args, **kwargs)

    def update_status(self, current_time=None):
        """Update meeting status based on current time"""
        if current_time is None:
            current_time = timezone.now()
            
        if self.status == 'scheduled' and self.start_time <= current_time <= self.end_time:
            self.status = 'ongoing'
            self.save()
        elif self.status in ['scheduled', 'ongoing'] and current_time > self.end_time:
            self.status = 'completed'
            self.save()
        
        return self.status

    class Meta:
        ordering = ['-created_at']
