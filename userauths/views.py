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

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.views.generic.edit import FormView
from django.contrib.auth import views as auth_views

class CustomPasswordResetForm(PasswordResetForm):
    def get_user(self):
        """
        Return a user matching the provided email.
        """
        email = self.cleaned_data['email']
        active_users = get_user_model().objects.filter(
            email__iexact=email,
            is_active=True,
        )
        if active_users.exists():
            return active_users.first()
        return None

class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        """
        Override form_valid to send a custom email for password reset.
        """
        user = form.get_user()
        site = get_current_site(self.request)
        
        context = {
            'email': user.email,
            'domain': site.domain,
            'site_name': site.name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
        
        subject = f'Password reset on {site.name}'
        email_template_name = 'userauths/password_reset_email.html'
        email_body = render_to_string(email_template_name, context)
        
        try:
            user.email_user(subject, email_body)
        except Exception as e:
            # Log the exception or handle it accordingly
            print(f"Error sending email: {e}")
        
        return super().form_valid(form)
    
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

def send_password_reset_email(request, user):
    current_site = get_current_site(request)  # Get the current site information
    subject = "Password Reset Requested"
    email_template_name = "userauths/password_reset_email.html"
    context = {
        'email': user.email,
        'domain': current_site.domain,  # This will be localhost:8000 if using development server
        'site_name': 'Enchanted Eden',
        'uid': user.pk,
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',  # Use 'https' if you are in production with an SSL certificate
    }
    email = render_to_string(email_template_name, context)
    user.email_user(subject, email)

from django.shortcuts import render, redirect
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

def password_reset_confirm_view(request, uidb64=None, token=None):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('userauths:password_reset_complete')
        else:
            form = SetPasswordForm(user)
    else:
        validlink = False
        form = None

    return render(request, 'userauths/password_reset_confirm.html', {
        'form': form,
        'validlink': validlink
    })
