from django.urls import path
from .views import (
    active_chat_session,
    book_session,
    check_availability,
    expert_list,
    chat_with_expert,
    phone_qa,
    reschedule_phone_call,
    my_bookings,
    cancel_session,
    rate_session,
    expert_sessions,
    expert_chat_session
)
app_name = 'expert_QA_session'
urlpatterns = [
    path('', expert_list, name='expert_list'),
    path('chat_with_expert/<int:expert_id>/', chat_with_expert, name='chat_with_expert'),
    path('phone_qa/<int:expert_id>/', phone_qa, name='phone_qa'),
    path('reschedule_phone_call/<int:session_id>/', reschedule_phone_call, name='reschedule_phone_call'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path('cancel_session/<int:session_id>/', cancel_session, name='cancel_session'),
    path('check_availability/<int:expert_id>/', check_availability, name='check_availability'),
    path('rate_session/<int:session_id>/', rate_session, name='rate_session'),
    path('book_session/<int:expert_id>/', book_session, name='book_session'),
    path('active_chat_session/<int:session_id>/', active_chat_session, name='active_chat_session'),
    path('expert/sessions/', expert_sessions, name='expert_sessions'),
    path('expert/chat/<int:session_id>/', expert_chat_session, name='expert_chat_session'),
]