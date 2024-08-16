from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Login
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'You have registered successfully! Please log in.')
            return redirect('userauths:login')
        else:
            messages.error(request, 'There was an error with your registration.')
    else:
        form = RegistrationForm()
    return render(request, 'userauths/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                
                # Update or create the login entry
                login_entry, created = Login.objects.get_or_create(user=user)
                login_entry.status = 'logged_in'
                login_entry.last_login = timezone.now()
                login_entry.login_count += 1
                login_entry.save()

                # Set session data
                request.session['user_id'] = user.id  # # Store user ID in session #
                request.session['first_name'] = user.first_name  # # Store first name in session #
                request.session['last_name'] = user.last_name  # # Store last name in session #
                request.session['email'] = user.email  # # Store email in session #

                return redirect('userauths:home')
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'userauths/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'userauths/home.html')

def logout(request):
    user = request.user
    if user.is_authenticated:
        # Update Login model to set status to 'logged_out'
        try:
            login_entry = Login.objects.get(user=user)
            login_entry.status = 'logged_out'
            login_entry.save()
        except ObjectDoesNotExist:
            # Handle the case where the login entry does not exist
            pass
        
        # Clear session data
        if 'user_id' in request.session:
            del request.session['user_id']  # # Clear user ID from session #
        if 'first_name' in request.session:
            del request.session['first_name']  # # Clear first name from session #
        if 'last_name' in request.session:
            del request.session['last_name']  # # Clear last name from session #
        if 'email' in request.session:
            del request.session['email']  # # Clear email from session #
    
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('userauths:login')

