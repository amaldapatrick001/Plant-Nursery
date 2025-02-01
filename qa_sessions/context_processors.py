from .models import QnASession
from django.utils import timezone

def notifications_context(request):
    if request.user.is_authenticated:
        upcoming_meetings = QnASession.objects.filter(
            customer=request.user,
            start_time__gte=timezone.now()
        ).order_by('start_time')
        return {'meetings': upcoming_meetings}
    return {}
