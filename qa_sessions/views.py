from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import QnASession
from .forms import ScheduleMeetingForm, ExpertScheduleMeetingForm
from .google_calendar import create_google_meet_event
from userauths.models import User_Reg, Expert
from django.utils import timezone  # Use this instead of datetime.timezone
from django.db.models import Case, When

def aschedule_meeting(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    if request.method == 'POST':
        form = ScheduleMeetingForm(request.POST)
        print("Form submitted:", request.POST)  # Debug print
        
        if form.is_valid():
            try:
                meeting = form.save(commit=False)
                
                # Get the user from session
                user_id = request.session.get('user_id')
                customer = User_Reg.objects.get(uid=user_id)
                
                # Verify expert exists
                expert_id = form.cleaned_data['expert'].expert_id
                expert = get_object_or_404(Expert, expert_id=expert_id)
                meeting.expert = expert
                
                # Set the max_participants from form
                meeting.max_participants = form.cleaned_data.get('max_participants', 10)
                meeting.current_participants = 1  # Start with 1 participant
                
                # Set the start and end times
                meeting.start_time = form.cleaned_data['start_time']
                meeting.end_time = form.cleaned_data['end_time']
                
                # Save the meeting first
                meeting.save()
                
                # Add the customer to the meeting
                meeting.customers.add(customer)
                messages.success(request, "Meeting scheduled successfully!")
                return redirect('qa_sessions:ameeting_list')
                
            except Expert.DoesNotExist:
                messages.error(request, "Selected expert does not exist!")
            except Exception as e:
                messages.error(request, f"Error scheduling meeting: {str(e)}")
        else:
            print("Form errors:", form.errors)  # Debug print
            
    else:
        form = ScheduleMeetingForm()

    # Get list of available experts for the form
    experts = Expert.objects.filter(availability_status='available')
    return render(request, 'qa_sessions/aschedule_meeting.html', {
        'form': form,
        'experts': experts
    })

def join_meeting(request, session_id):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
        
    try:
        session = QnASession.objects.get(pk=session_id)
        user_id = request.session.get('user_id')
        customer = User_Reg.objects.get(uid=user_id)
        
        if session.add_customer(customer):
            messages.success(request, "Successfully joined the meeting!")
        else:
            messages.error(request, "Meeting is full!")
            
        return redirect('qa_sessions:ameeting_detail', session_id=session_id)
    except QnASession.DoesNotExist:
        messages.error(request, "Meeting not found!")
        return redirect('qa_sessions:ameeting_list')

def eview_scheduled_meetings(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
        
    # Get the expert associated with the logged-in user
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    expert = get_object_or_404(Expert, user=user)
    
    # Filter meetings by the expert and order by status and start time
    meetings = QnASession.objects.filter(expert=expert).order_by(
        Case(
            When(status='scheduled', then=1),
            When(status='ongoing', then=2),
            When(status='completed', then=3),
            When(status='cancelled', then=4),
            default=5,
        ),
        'start_time'
    )
    
    # Organize meetings by status
    scheduled_meetings = meetings.filter(status='scheduled')
    ongoing_meetings = meetings.filter(status='ongoing')
    completed_meetings = meetings.filter(status='completed')
    cancelled_meetings = meetings.filter(status='cancelled')
    
    context = {
        'scheduled_meetings': scheduled_meetings,
        'ongoing_meetings': ongoing_meetings,
        'completed_meetings': completed_meetings,
        'cancelled_meetings': cancelled_meetings,
    }
    
    return render(request, 'qa_sessions/eview_scheduled_meetings.html', context)


def ameeting_list(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
    
    current_time = timezone.now()
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    
    # Update meeting statuses first
    all_meetings = QnASession.objects.all()
    for meeting in all_meetings:
        # Update status based on current time
        if meeting.status == 'scheduled' and meeting.start_time <= current_time <= meeting.end_time:
            meeting.status = 'ongoing'
            meeting.save()
        elif meeting.status in ['scheduled', 'ongoing'] and current_time > meeting.end_time:
            meeting.status = 'completed'
            meeting.save()
    
    # Get meetings based on user type
    if hasattr(user, 'expert'):
        # For experts: show their own meetings
        meetings = QnASession.objects.filter(
            expert=user.expert
        ).select_related('expert', 'expert__user').prefetch_related('customers')
    else:
        # For customers: show meetings they're registered for
        meetings = QnASession.objects.filter(
            customers=user
        ).select_related('expert', 'expert__user').prefetch_related('customers')
    
    # Separate meetings by status
    scheduled_meetings = meetings.filter(status='scheduled').order_by('start_time')
    ongoing_meetings = meetings.filter(status='ongoing').order_by('start_time')
    completed_meetings = meetings.filter(status='completed').order_by('-start_time')
    cancelled_meetings = QnASession.objects.filter(status='cancelled').order_by('-start_time')
    
    context = {
        'scheduled_meetings': scheduled_meetings,
        'ongoing_meetings': ongoing_meetings,
        'completed_meetings': completed_meetings,
        'cancelled_meetings': cancelled_meetings,
        'current_time': current_time,
        'user': user
    }
    
    return render(request, 'qa_sessions/ameeting_list.html', context)

def ameeting_detail(request, session_id):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
        
    current_time = timezone.now()
    meeting = get_object_or_404(QnASession, session_id=session_id)
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    
    # Update meeting status
    meeting.update_status(current_time)
    
    context = {
        'meeting': meeting,
        'current_time': current_time,
        'user': user,
        'is_expert': hasattr(user, 'expert') and user.expert == meeting.expert,
        'is_participant': user in meeting.customers.all()
    }
    
    return render(request, 'qa_sessions/ameeting_detail.html', context)

def cancel_meeting(request, session_id):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
        
    meeting = get_object_or_404(QnASession, session_id=session_id)
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    
    # Check if user is either an admin or the expert who created the meeting
    is_admin = user.user_type.usertype.lower() == 'admin'  # Check UserType
    is_expert = hasattr(user, 'expert') and user.expert == meeting.expert
    
    if not (is_admin or is_expert):
        messages.error(request, 'You do not have permission to cancel this meeting.')
        return redirect('qa_sessions:ameeting_list')
    
    # Check if meeting hasn't started yet
    current_time = timezone.now()
    if current_time >= meeting.start_time:
        messages.error(request, 'Cannot cancel a meeting that has already started.')
        return redirect('qa_sessions:ameeting_list')
    
    try:
        # Notify all participants about cancellation
        for participant in meeting.customers.all():
            # Here you could add email notification logic
            pass
            
        meeting.status = 'cancelled'
        meeting.save()
        messages.success(request, 'Meeting cancelled successfully. All participants will be notified.')
        
    except Exception as e:
        messages.error(request, f'Error cancelling meeting: {str(e)}')
        
    return redirect('qa_sessions:ameeting_list')












def view_customer_notifications(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
        
    current_time = timezone.now()
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    
    # Update meeting statuses first
    all_meetings = QnASession.objects.all()
    for meeting in all_meetings:
        if meeting.status == 'scheduled' and meeting.start_time <= current_time <= meeting.end_time:
            meeting.status = 'ongoing'
            meeting.save()
        elif meeting.status in ['scheduled', 'ongoing'] and current_time > meeting.end_time:
            meeting.status = 'completed'
            meeting.save()
    
    # Get all scheduled meetings
    scheduled_meetings = QnASession.objects.filter(
        status='scheduled'
    ).select_related('expert', 'expert__user').prefetch_related('customers').order_by('start_time')
    
    # Get ongoing meetings
    ongoing_meetings = QnASession.objects.filter(
        status='ongoing',
        end_time__gt=current_time
    ).select_related('expert', 'expert__user').prefetch_related('customers').order_by('start_time')
    
    # Get user's booked sessions
    booked_sessions = QnASession.objects.filter(
        customers=user
    ).values_list('session_id', flat=True)
    
    context = {
        'scheduled_meetings': scheduled_meetings,
        'ongoing_meetings': ongoing_meetings,
        'current_time': current_time,
        'user': user,
        'booked_sessions': list(booked_sessions)  # Convert to list for template comparison
    }
    
    return render(request, 'qa_sessions/customer_notifications.html', context)

def book_slot(request, session_id):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to book a slot.')
        return redirect('userauths:login')
        
    if request.method == 'POST':
        meeting = get_object_or_404(QnASession, session_id=session_id)
        user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
        
        # Check if user already has a slot in this meeting
        if user in meeting.customers.all():
            messages.warning(request, 'You have already booked a slot for this session!')
            return redirect('qa_sessions:customer_notifications')
            
        # Check if user has any other slots at the same time
        conflicting_meetings = QnASession.objects.filter(
            customers=user,
            start_time__lt=meeting.end_time,
            end_time__gt=meeting.start_time
        )
        
        if conflicting_meetings.exists():
            messages.error(request, 'You already have a session scheduled during this time!')
            return redirect('qa_sessions:customer_notifications')
        
        if meeting.current_participants < meeting.max_participants:
            meeting.customers.add(user)
            meeting.current_participants += 1
            meeting.save()
            messages.success(request, 'Slot booked successfully! You can cancel this booking if needed.')
        else:
            messages.error(request, 'Sorry, this session is full.')
            
    return redirect('qa_sessions:customer_notifications')

def remove_slot(request, session_id):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to manage your bookings.')
        return redirect('userauths:login')
        
    if request.method == 'POST':
        meeting = get_object_or_404(QnASession, session_id=session_id)
        user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
        
        # Check if user actually has a slot in this meeting
        if user not in meeting.customers.all():
            messages.error(request, 'You do not have a slot in this session.')
            return redirect('qa_sessions:customer_notifications')
            
        # Check if the meeting hasn't started yet
        current_time = timezone.now()
        if current_time >= meeting.start_time:
            messages.error(request, 'Cannot cancel slot after session has started.')
            return redirect('qa_sessions:customer_notifications')
        
        meeting.customers.remove(user)
        meeting.current_participants -= 1
        meeting.save()
        
        messages.success(request, 'Slot cancelled successfully! You can book again if needed.')
            
    return redirect('qa_sessions:customer_notifications')

def eview_meeting_detail(request, session_id):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
        
    # Get the expert associated with the logged-in user
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    expert = get_object_or_404(Expert, user=user)
    
    # Get the meeting and verify it belongs to this expert
    meeting = get_object_or_404(QnASession, session_id=session_id, expert=expert)
    
    # Update meeting status based on current time
    current_time = timezone.now()
    if meeting.status == 'scheduled' and meeting.start_time <= current_time <= meeting.end_time:
        meeting.status = 'ongoing'
        meeting.save()
    elif meeting.status in ['scheduled', 'ongoing'] and current_time > meeting.end_time:
        meeting.status = 'completed'
        meeting.save()
    
    context = {
        'meeting': meeting,
        'current_time': current_time,
        'user': user,
        'is_expert': True,  # Since we've verified this is the expert's meeting
        'participants': meeting.customers.all().select_related('user_type')
    }
    
    return render(request, 'qa_sessions/eview_meeting_detail.html', context)

def eschedule_meeting(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')
    
    # Get the expert associated with the logged-in user
    user = get_object_or_404(User_Reg, uid=request.session.get('user_id'))
    expert = get_object_or_404(Expert, user=user)
    
    if request.method == 'POST':
        form = ExpertScheduleMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.expert = expert
            meeting.current_participants = 0
            meeting.status = 'scheduled'
            
            # Create Google Meet link (if you have Google Calendar integration)
            try:
                google_meet_service = GoogleMeetService()
                meeting.google_meet_link = google_meet_service.create_meeting(
                    meeting.title,
                    meeting.start_time,
                    meeting.end_time
                )
            except Exception as e:
                # Handle the error appropriately
                messages.warning(request, "Meeting created but Google Meet link couldn't be generated.")
            
            meeting.save()
            messages.success(request, "Meeting scheduled successfully!")
            return redirect('qa_sessions:eview_scheduled_meetings')
    else:
        form = ExpertScheduleMeetingForm()
    
    return render(request, 'qa_sessions/eschedule_meeting.html', {
        'form': form,
        'expert': expert
    })
