from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse_lazy
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import Login, User_Reg, UserType
from .forms import RegistrationForm, CustomPasswordResetForm, CustomSetPasswordForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            if Login.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please use a different email address.')
                return redirect('userauths:register')

            # Save the user
            user = form.save(commit=False)
            user.user_type = UserType.objects.get(utid=2)  # Assuming UserType is correctly set
            user.status = True
            user.save()

            # Create the Login entry with the hashed password
            Login.objects.create(
                uid=user,
                email=email,
                password=make_password(password1),  # Ensure the password is hashed
                login_count=0,
                status=False
            )

            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('userauths:login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'userauths/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')  # This should be the raw password input by the user

        try:
            # Fetch the Login record
            user_login = Login.objects.get(email=email)

            # Authenticate using the raw password
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Successful authentication
                auth_login(request, user)

                # Update login details
                user_login.login_count += 1
                user_login.last_login = timezone.now()
                user_login.save()

                # Store additional information in the session
                request.session['user_id'] = user_login.login_id
                request.session['user_first_name'] = user_login.uid.first_name
                request.session['user_last_name'] = user_login.uid.last_name
                request.session['email'] = user_login.email

                # Redirect based on user type
                user_type = user_login.uid.user_type_id
                if user_type == 1:
                    return redirect('admin_dashboard')
                elif user_type == 2:
                    return redirect('userauths:index')
                elif user_type == 3:
                    return redirect('delivery_dashboard')
                elif user_type == 4:
                    return redirect('expert_dashboard')
                else:
                    messages.error(request, 'User type is not recognized.')
            else:
                # Authentication failed
                messages.error(request, 'Incorrect  password.')

        except Login.DoesNotExist:
            messages.error(request, 'No account found with this email.')

    return render(request, 'userauths/login.html')



@transaction.atomic
def logout(request):
    if request.user.is_authenticated:
        try:
            # Fetch the user registration and login entries
            user_reg = User_Reg.objects.get(first_name=request.user.first_name, last_name=request.user.last_name)
            login_entry = Login.objects.get(uid=user_reg)

            # Update last_logout and status
            login_entry.last_logout = timezone.now()
            login_entry.status = False
            login_entry.save()

        except User_Reg.DoesNotExist:
            messages.error(request, 'User registration record not found.')
        except Login.DoesNotExist:
            messages.error(request, 'Login entry not found.')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')

        # Perform logout and flush the session
        auth_logout(request)
        request.session.flush()

        # Notify the user
        messages.info(request, 'You have been logged out.')

    return redirect('userauths:index')

from django.views.generic import TemplateView
class IndexView(TemplateView):
    template_name = 'core/index.html'
class adminindex(TemplateView):
    template_name="core/adminindex.html"


def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Login.objects.get(email=email)
            except Login.DoesNotExist:
                messages.error(request, 'No user is associated with this email.')
                return redirect('userauths:password_reset_form')

            # Generate token and UID for password reset
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Send password reset email
            current_site = get_current_site(request)
            subject = 'Password Reset Requested'
            message = render_to_string('userauths/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(subject, message, 'admin@example.com', [user.email], fail_silently=False)

            # Redirect to password reset done page
            return redirect('userauths:password_reset_done')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'userauths/password_reset_form.html', {'form': form})



def password_reset_confirm(request, uidb64=None, token=None, *args, **kwargs):
    error_message = None

    try:
        # Decode the uid from base64 to retrieve the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None
        error_message = str(e)

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            # If it's a POST request, process the form submission
            form = CustomSetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()  # Save the new password
                return redirect('password_reset_complete')  # Redirect after success
        else:
            # If it's a GET request, display the form
            form = CustomSetPasswordForm(user=user)
        
        return TemplateResponse(request, 'userauths/password_reset_confirm.html', {
            'form': form,
            'uid': uidb64,
            'token': token,
        })
    else:
        # If the user is None or the token is invalid, display the error message
        if not error_message:
            error_message = "The reset link is invalid or has expired. Please try resetting your password again."
        return TemplateResponse(request, 'userauths/password_reset_confirm.html', {
            'error_message': error_message,
        })
