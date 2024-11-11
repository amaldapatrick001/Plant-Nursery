from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100, help_text="Enter your name")
    email = models.EmailField(max_length=100, help_text="Enter your email")
    subject = models.CharField(max_length=100, help_text="Enter the subject")
    message = models.TextField(help_text="Enter your message")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_responded = models.BooleanField(default=False, help_text="Indicates if a response has been sent")

    def __str__(self):
        return f'{self.name} - {self.subject}'