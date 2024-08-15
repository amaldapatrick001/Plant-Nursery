from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
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
    auth_logout(request)
    return redirect('userauths:login')
