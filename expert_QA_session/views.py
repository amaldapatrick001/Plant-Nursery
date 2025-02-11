from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import  ExpertSession, ChatMessage
from userauths.models import User_Reg, Expert
from django.utils import timezone
from datetime import timedelta
from .asterisk_utils import AsteriskHandler
from django.db.models import Avg
from django.core.exceptions import ValidationError
import json
from django.db import models

def check_auth(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('userauths:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@check_auth
def expert_list(request):
    experts = Expert.objects.filter(availability_status='available')
    return render(request, 'expert_QA_session/expert_list.html', {'experts': experts})

@check_auth
def chat_with_expert(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    user = get_object_or_404(User_Reg, uid=request.session['user_id'])
    
    # Check for active session
    now = timezone.now()
    active_session = ExpertSession.objects.filter(
        expert=expert,
        user=user,
        session_type='chat',
        session_date__lte=now,
        session_date__gte=now - timezone.timedelta(minutes=expert.session_duration)
    ).first()
    
    messages = ChatMessage.objects.filter(
        sender=user, recipient=expert.user
    ) | ChatMessage.objects.filter(
        sender=expert.user, recipient=user
    ).order_by('timestamp')

    return render(request, 'expert_QA_session/chat.html', {
        'expert': expert, 
        'messages': messages,
        'active_session': active_session
    })

@check_auth
def phone_qa(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    user = get_object_or_404(User_Reg, uid=request.session['user_id'])
    
    return render(request, 'expert_QA_session/phone_qa.html', {
        'expert': expert,
        'user': user
    })

def schedule_call_reminders(session):
    """Schedule call reminders with error handling for missing Asterisk config"""
    try:
        asterisk = AsteriskHandler()
        call_id = asterisk.schedule_call(
            session.user.phoneno,
            session.expert.contact_phone
        )
        return call_id
    except AttributeError:
        # If Asterisk settings are not configured, return a dummy call_id
        return f"CALL_{session.session_id}"
    except Exception as e:
        print(f"Warning: Could not schedule call reminder: {str(e)}")
        return f"CALL_{session.session_id}"

@check_auth
def reschedule_phone_call(request, session_id):
    user = get_object_or_404(User_Reg, uid=request.session['user_id'])
    session = get_object_or_404(ExpertSession, session_id=session_id, user=user)

    if session.session_date < timezone.now():
        return JsonResponse({"error": "Cannot reschedule past sessions."}, status=400)

    if request.method == "POST":
        new_date = request.POST.get("new_date")
        new_datetime = timezone.datetime.strptime(new_date, "%Y-%m-%dT%H:%M")

        # Check if new slot is available
        overlapping_sessions = ExpertSession.objects.filter(
            expert=session.expert,
            session_date__lte=new_datetime + timedelta(minutes=9),
            session_date__gte=new_datetime
        ).exclude(pk=session.session_id).exists()

        if overlapping_sessions:
            return JsonResponse({"error": "This time slot is already booked."}, status=400)

        # Update session date
        session.session_date = new_datetime
        session.save()

        return JsonResponse({"message": "Session rescheduled successfully!"})

    return render(request, 'expert_QA_session/reschedule_phone_call.html', {'session': session})

@check_auth
def my_bookings(request):
    user = get_object_or_404(User_Reg, uid=request.session['user_id'])
    now = timezone.now()
    
    upcoming_sessions = ExpertSession.objects.filter(
        user=user,
        session_date__gte=now
    ).order_by('session_date')
    
    past_sessions = ExpertSession.objects.filter(
        user=user,
        session_date__lt=now
    ).order_by('-session_date')
    
    return render(request, 'expert_QA_session/my_bookings.html', {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions
    })

@check_auth
def cancel_session(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(
            ExpertSession, 
            session_id=session_id,
            user__uid=request.session['user_id']
        )
        
        if session.is_past:
            return JsonResponse({
                'success': False,
                'error': 'Cannot cancel past sessions'
            })
            
        session.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@check_auth
def rate_session(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(
            ExpertSession, 
            session_id=session_id,
            user__uid=request.session['user_id'],
            session_date__lt=timezone.now()
        )
        
        try:
            rating = int(request.POST.get('rating'))
            if 1 <= rating <= 5:
                session.rating = rating
                session.is_rated = True
                session.save()
                
                # Update expert's average rating
                expert = session.expert
                expert.rating = (
                    ExpertSession.objects.filter(
                        expert=expert,
                        is_rated=True
                    ).aggregate(Avg('rating'))['rating__avg']
                )
                expert.save()
                
                return JsonResponse({'success': True})
        except (ValueError, TypeError):
            pass
            
        return JsonResponse({
            'success': False,
            'error': 'Invalid rating value'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@check_auth
def check_availability(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    date = request.GET.get('date')
    
    try:
        # Convert date string to datetime
        date_obj = timezone.datetime.strptime(date, "%Y-%m-%d").date()
        
        # Get day of week in lowercase
        day_of_week = date_obj.strftime('%A').lower()
        
        # Get schedule for that day from availability_schedule
        schedule = expert.availability_schedule or {}
        day_schedule = schedule.get(day_of_week, {})
        
        if not day_schedule.get('available', False):
            return JsonResponse({'available_slots': []})
        
        # Get start and end hours
        start_time = timezone.datetime.strptime(day_schedule.get('start', '09:00'), '%H:%M')
        end_time = timezone.datetime.strptime(day_schedule.get('end', '17:00'), '%H:%M')
        
        # Get all existing sessions for that date
        existing_sessions = ExpertSession.objects.filter(
            expert=expert,
            session_date__date=date_obj
        ).order_by('session_date')
        
        # Calculate available slots
        available_slots = []
        current_time = timezone.now()
        
        # Generate slots every 30 minutes
        slot_time = timezone.datetime.combine(
            date_obj,
            start_time.time()
        )
        slot_time = timezone.make_aware(slot_time)
        
        while slot_time.time() <= end_time.time():
            # Skip slots in the past
            if slot_time <= current_time:
                slot_time += timezone.timedelta(minutes=30)
                continue
            
            # Check if slot overlaps with any existing session
            is_available = True
            slot_end = slot_time + timezone.timedelta(minutes=expert.session_duration)
            
            for session in existing_sessions:
                session_end = session.session_date + timezone.timedelta(minutes=expert.session_duration)
                if (slot_time < session_end and slot_end > session.session_date):
                    is_available = False
                    break
            
            if is_available:
                # Just append the time string instead of a complex object
                available_slots.append(slot_time.strftime("%H:%M"))
            
            slot_time += timezone.timedelta(minutes=30)
        
        return JsonResponse({'available_slots': available_slots})
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=400)

@check_auth
def book_session(request, expert_id):
    expert = get_object_or_404(Expert, pk=expert_id)
    user = get_object_or_404(User_Reg, uid=request.session['user_id'])

    if request.method == "POST":
        session_type = request.POST.get('session_type')
        session_date = request.POST.get('session_date')
        session_time = request.POST.get('session_time', '')  # For phone calls

        try:
            # Combine date and time for phone calls
            if session_type == 'call' and session_time:
                session_datetime = timezone.datetime.strptime(
                    f"{session_date} {session_time}",
                    "%Y-%m-%d %H:%M"
                )
            else:
                session_datetime = timezone.datetime.strptime(session_date, "%Y-%m-%dT%H:%M")
            
            session_datetime = timezone.make_aware(session_datetime)
            
            # Check for overlapping sessions (both chat and call)
            session_end = session_datetime + timezone.timedelta(minutes=expert.session_duration)
            overlapping_sessions = ExpertSession.objects.filter(
                expert=expert,
                session_date__lt=session_end,
                session_date__gt=session_datetime - timezone.timedelta(minutes=expert.session_duration)
            ).exists()

            if overlapping_sessions:
                return JsonResponse({
                    "error": "This time slot is no longer available. Please choose another time."
                })

            # Create session
            session = ExpertSession.objects.create(
                expert=expert,
                user=user,
                session_type=session_type,
                session_date=session_datetime
            )

            # Schedule call reminders for phone sessions
            if session_type == 'call':
                call_id = schedule_call_reminders(session)
                session.call_id = call_id
                session.save()

            return JsonResponse({
                "success": True,
                "message": f"{session_type.title()} session scheduled successfully!",
                "session_id": session.session_id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return render(request, 'expert_QA_session/book_session.html', {
        'expert': expert
    })

# Add a view for experts to set their schedule
@check_auth
def set_expert_schedule(request, expert_id):
    if request.method == 'POST':
        expert = get_object_or_404(Expert, pk=expert_id)
        schedule_data = request.POST.get('schedule')
        
        try:
            schedule_dict = json.loads(schedule_data)
            expert.set_weekly_schedule(schedule_dict)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@check_auth
def active_chat_session(request, session_id):
    # Get the session and verify user's access
    session = get_object_or_404(ExpertSession, session_id=session_id)
    user = get_object_or_404(User_Reg, uid=request.session['user_id'])
    
    # Verify this is the user's session
    if session.user != user:
        messages.error(request, 'You do not have access to this chat session.')
        return redirect('expert_QA_session:my_bookings')
    
    # Check if session is active
    now = timezone.now()
    session_end_time = session.session_date + timezone.timedelta(minutes=session.expert.session_duration)
    
    is_active = session.session_date <= now <= session_end_time
    is_upcoming = session.session_date > now
    
    # Get chat messages for this session
    chat_messages = ChatMessage.objects.filter(
        models.Q(sender=user, recipient=session.expert.user) |
        models.Q(sender=session.expert.user, recipient=user)
    ).order_by('timestamp')
    
    context = {
        'session': session,
        'expert': session.expert,
        'messages': chat_messages,
        'is_active': is_active,
        'is_upcoming': is_upcoming,
        'session_end_time': session_end_time,
    }
    
    return render(request, 'expert_QA_session/active_chat_session.html', context)

@check_auth
def expert_sessions(request):
    # Get the expert
    expert = get_object_or_404(Expert, user__uid=request.session['user_id'])
    
    # Get current time
    now = timezone.now()
    
    # Get upcoming sessions
    upcoming_sessions = ExpertSession.objects.filter(
        expert=expert,
        session_date__gt=now
    ).order_by('session_date')
    
    # Get active sessions
    active_sessions = ExpertSession.objects.filter(
        expert=expert,
        session_date__lte=now,
        session_date__gte=now - timezone.timedelta(minutes=expert.session_duration)
    ).order_by('session_date')
    
    # Get past sessions
    past_sessions = ExpertSession.objects.filter(
        expert=expert,
        session_date__lt=now - timezone.timedelta(minutes=expert.session_duration)
    ).order_by('-session_date')
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'active_sessions': active_sessions,
        'past_sessions': past_sessions,
    }
    
    return render(request, 'expert_QA_session/expert_sessions.html', context)

@check_auth
def expert_chat_session(request, session_id):
    # Get the expert
    expert = get_object_or_404(Expert, user__uid=request.session['user_id'])
    
    # Get the session
    session = get_object_or_404(ExpertSession, session_id=session_id, expert=expert)
    
    # Check if session is active
    now = timezone.now()
    session_end_time = session.session_date + timezone.timedelta(minutes=expert.session_duration)
    
    is_active = session.session_date <= now <= session_end_time
    is_upcoming = session.session_date > now
    
    # Get chat messages
    chat_messages = ChatMessage.objects.filter(
        models.Q(sender=session.user, recipient=expert.user) |
        models.Q(sender=expert.user, recipient=session.user)
    ).order_by('timestamp')
    
    context = {
        'session': session,
        'user': session.user,
        'messages': chat_messages,
        'is_active': is_active,
        'is_upcoming': is_upcoming,
        'session_end_time': session_end_time,
    }
    
    return render(request, 'expert_QA_session/expert_chat_session.html', context)