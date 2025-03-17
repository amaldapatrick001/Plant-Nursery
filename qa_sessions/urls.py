from django.urls import path
from . import views

app_name = 'qa_sessions'

urlpatterns = [
    path('schedule/', views.aschedule_meeting, name='schedule_meeting'),
    path('meetings/', views.ameeting_list, name='ameeting_list'),
    path('meetings/<int:session_id>/', views.ameeting_detail, name='ameeting_detail'),
    path('meetings/<int:session_id>/join/', views.join_meeting, name='join_meeting'),
    path('meetings/<int:session_id>/cancel/', views.cancel_meeting, name='cancel_meeting'),
    path('notifications/', views.view_customer_notifications, name='customer_notifications'),
    path('my-meetings/', views.eview_scheduled_meetings, name='eview_scheduled_meetings'),
    path('book-slot/<int:session_id>/', views.book_slot, name='book_slot'),
    path('remove-slot/<int:session_id>/', views.remove_slot, name='remove_slot'),
    path('expert/meetings/', views.eview_scheduled_meetings, name='eview_scheduled_meetings'),
    path('expert/meeting/<str:session_id>/', views.eview_meeting_detail, name='eview_meeting_detail'),
   path('expert/schedule/', views.eschedule_meeting, name='eschedule_meeting'),  # Changed from 'schedule_meeting' to 'eschedule_meeting'
]