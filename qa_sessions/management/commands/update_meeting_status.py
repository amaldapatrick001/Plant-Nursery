from django.core.management.base import BaseCommand
from django.utils import timezone
from qa_sessions.models import QnASession

class Command(BaseCommand):
    help = 'Updates meeting statuses based on their start and end times'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # Update to 'ongoing' for meetings that have started
        QnASession.objects.filter(
            status='scheduled',
            start_time__lte=now,
            end_time__gt=now
        ).update(status='ongoing')

        # Update to 'completed' for meetings that have ended
        QnASession.objects.filter(
            status='ongoing',
            end_time__lte=now
        ).update(status='completed')

        self.stdout.write(self.style.SUCCESS('Successfully updated meeting statuses')) 