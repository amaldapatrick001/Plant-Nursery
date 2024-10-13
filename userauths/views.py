from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render, redirect
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
from rapidfuzz import fuzz

from PlantNursery import settings

from .models import Login, User_Reg, UserType
from django.views.decorators.cache import cache_control
from .forms import RegistrationForm, CustomPasswordResetForm, CustomSetPasswordForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .models import Login, UserType

from django.core.mail import send_mail
from django.conf import settings

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            if Login.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please use a different email address.')
                return render(request, 'userauths/register.html', {'form': form, 'status': 'error'})

            # Save the user
            user = form.save(commit=False)
            user.user_type = UserType.objects.get(utid=2)  # Assuming UserType is correctly set
            user.status = True
            user.save()

            # Create the Login entry with the hashed password
            user_login = Login.objects.create(
                uid=user,
                email=email,
                login_count=0,
                status=False  # Initially not logged in
            )

            # Set the password using the model's method
            user_login.set_password(password1)
            user_login.save()

            # Send registration email
            send_registration_email(user_login)

            messages.success(request, 'Registration successful. You can now log in.')
            return render(request, 'userauths/register.html', {'form': form, 'status': 'success'})
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
            return render(request, 'userauths/register.html', {'form': form, 'status': 'error'})
    else:
        form = RegistrationForm()

    return render(request, 'userauths/register.html', {'form': form})

def send_registration_email(user_login):
    """Send an email notification upon successful registration."""
    subject = "Welcome to Enchanted Eden!"
    message = (
        f"Dear {user_login.uid.first_name},\n\n"
        "Thank you for registering with Enchanted Eden. Your account has been successfully created.\n\n"
        "You can now log in and explore our services.\n\n"
        "Best Regards,\n"
        "The Enchanted Eden Team\n"
        "For further details, please contact us at support@enchantededen.com."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_login.email],
        fail_silently=False,
    )
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_login = Login.objects.get(email=email)

            if user_login.status:
                messages.error(request, 'This account is already logged in from another session.')
                return redirect('userauths:login')

            if user_login.check_password(password):
                # Successful authentication
                user_login.login()

                # Set user information in session
                request.session['user_id'] = user_login.login_id 
                request.session['user_first_name'] = user_login.uid.first_name
                request.session['user_last_name'] = user_login.uid.last_name
                request.session['email'] = user_login.email  # Save email in session
                request.session['is_authenticated'] = True

                # Send login notification email
                send_login_email(user_login)

                # Redirect based on user type
                user_type = user_login.uid.user_type_id
                if user_type == 1:
                    return redirect('userauths:adminindex')
                elif user_type == 2:
                    return redirect('userauths:index')
                elif user_type == 3:
                    return redirect('delivery_dashboard')
                elif user_type == 4:
                    return redirect('expert_dashboard')
                else:
                    messages.error(request, 'User type is not recognized.')
                    return redirect('userauths:login')
            else:
                messages.error(request, 'Incorrect password.')
        except Login.DoesNotExist:
            messages.error(request, 'No account found with this email.')

    return render(request, 'userauths/login.html')

def send_login_email(user_login):
    """Send an email notification upon successful login."""
    subject = "Login Notification - Enchanted Eden"
    message = (
        f"Dear {user_login.uid.first_name},\n\n"
        "You have successfully logged into your Enchanted Eden account. If this wasn't you, please contact our support team immediately.\n\n"
        "Best Regards,\n"
        "The Enchanted Eden Team\n"
        "For further details, please contact us at support@enchantededen.com."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_login.email],
        fail_silently=False,
    )



from django.contrib.auth import logout as auth_logout
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@transaction.atomic
@never_cache
def logout(request):
    # Get the current page URL to redirect back to it after logout
    redirect_url = request.META.get('HTTP_REFERER', reverse('userauths:index'))  # Fallback to index if referer is not available
    
    # Ensure the redirect URL is safe
    if not url_has_allowed_host_and_scheme(redirect_url, allowed_hosts={request.get_host()}):
        redirect_url = reverse('userauths:index')

    if 'is_authenticated' in request.session and request.session['is_authenticated']:
        try:
            # Fetch the user registration and login entries
            user_reg = User_Reg.objects.get(
                first_name=request.session['user_first_name'], 
                last_name=request.session['user_last_name']
            )
            login_entry = Login.objects.get(uid=user_reg)

            # Update last_logout and status
            login_entry.logout()  # This sets status to False and updates last_logout
            messages.success(request, 'You have been successfully logged out.')
        except User_Reg.DoesNotExist:
            messages.error(request, 'User registration record not found.')
        except Login.DoesNotExist:
            messages.error(request, 'Login entry not found.')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')

        # Perform logout and flush the session
        auth_logout(request)
        request.session.flush()

    # Redirect back to the page where the logout request was made, with the logout message
    return redirect(redirect_url)



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User_Reg, Login
from .forms import UpdateProfileForm, UpdatePasswordForm

def update_profile(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('userauths:login')

    try:
        user_login = Login.objects.get(login_id=request.session['user_id'])
        user = user_login.uid
    except Login.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('userauths:login')

    # Initialize the forms
    profile_form = UpdateProfileForm(instance=user)
    password_form = UpdatePasswordForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        print("Action:", action)  # Log action
        print("POST Data:", request.POST)  # Log all POST data

        if action == 'update_profile':
            # Handle profile update
            profile_form = UpdateProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                print("Profile form saved successfully")
                messages.success(request, 'Profile updated successfully!')
            else:
                print("Profile form validation failed", profile_form.errors)


        elif action == 'update_password':
            # Handle password update
            password_form = UpdatePasswordForm(request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password']
                user_login.set_password(new_password)
                user_login.save()
                print("Password updated in the database")  # Log success
                messages.success(request, 'Password updated successfully!')
            else:
                print("Password form validation failed", password_form.errors)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'userauths/update_profile.html', context)






from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

# Apply cache control to the class-based view
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class IndexView(TemplateView):
    template_name = 'core/index.html'

    
from django.db.models import Count
from django.shortcuts import render
from .models import User_Reg # Assuming these are in the current app
from products.models import Product  # Import Product from the 'product' app


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class adminindex(TemplateView):
    template_name = "core/adminindex.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the count of users, products, and orders, setting to 0 if no data exists
        context['user_count'] = User_Reg.objects.count() if User_Reg.objects.exists() else 0
        context['product_count'] = Product.objects.count() if Product.objects.exists() else 0
        
        return context




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
    validlink = False  # Default to False

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Login.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Login.DoesNotExist) as e:
        user = None
        error_message = str(e)

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True  # Set validlink to True if token and user are valid

        if request.method == 'POST':
            form = CustomSetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()  # Save the new password
                return redirect('userauths:password_reset_complete')

        else:
            form = CustomSetPasswordForm(user=user)
        
        return render(request, 'userauths/password_reset_confirm.html', {
            'form': form,
            'validlink': validlink,
            'uid': uidb64,
            'token': token,
        })
    else:
        if not error_message:
            error_message = "The reset link is invalid or has expired. Please try resetting your password again."
        return render(request, 'userauths/password_reset_confirm.html', {
            'error_message': error_message,
            'validlink': validlink
        })






    
# myproject/userauths/views.py
from django.shortcuts import render
from .models import User_Reg

def user_details(request):
    # Fetch users with related login and usertype data
    users = User_Reg.objects.select_related('user_type').prefetch_related('login_set').all()

    # Prepare user data for template
    user_data = []
    for user in users:
        login = user.login_set.first()  # Get the related login info
        user_data.append({
            'name': f'{user.first_name} {user.last_name}',
            'phoneno': user.phoneno,
            'email': login.email if login else '',
            'registration_date': user.date_time_reg,
            'last_login': login.last_login if login else '',
            'login_count': login.login_count if login else 0,
            'user_type': user.user_type.usertype if user.user_type else '',
            'status': 'Active' if user.status else 'Inactive'
        })

    return render(request, 'userauths/user_details.html', {'users': user_data})




def user_details_view(request):
    # Fetch active users with related login data
    active_users = User_Reg.objects.filter(status=True).prefetch_related('login_set')
    deleted_users = User_Reg.objects.filter(status=False).prefetch_related('login_set')

    # Prepare user login info for both active and deleted users
    logins = Login.objects.all()

    return render(request, 'userauths/user_del_restor.html', {
        'active_users': active_users,
        'deleted_users': deleted_users,
        'logins': logins
    })

def send_activation_email(user, action):
    """Send an email notification to the user regarding activation/deactivation."""
    try:
        subject = f"Your account with Enchanted Eden has been {action}"

        if action == 'deactivated':
            message = (
                "Dear User,\n\n"
                "We regret to inform you that your account with Enchanted Eden has been deactivated. "
                "If you believe this is a mistake, or if you have any questions, please contact our support team.\n\n"
                "Thank you for being a valued member of the Enchanted Eden community!\n\n"
                "Best Regards,\n"
                "The Enchanted Eden Team\n"
                "For further details, please contact us at support@enchantededen.com."
            )
        else:  # For activation
            message = (
                "Dear User,\n\n"
                "Great news! Your account with Enchanted Eden has been reactivated. "
                "You can now log in and enjoy our services once again. If you have any questions, please reach out to our support team.\n\n"
                "Thank you for being a valued member of the Enchanted Eden community!\n\n"
                "Best Regards,\n"
                "The Enchanted Eden Team\n"
                "For further details, please contact us at support@enchantededen.com."
            )

        # Send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.login_set.first().email],  # Assumes there's a related login entry with an email
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


def delete_user_view(request, uid):
    # Soft delete user by setting status to False
    user = get_object_or_404(User_Reg, uid=uid)
    user.status = False
    user.save()

    # Send deactivation email
    send_activation_email(user, action='deactivated')

    return redirect('userauths:user_details_view')  # Redirect back to the user details page

def undo_delete_view(request, uid):
    # Restore user by setting status to True
    user = get_object_or_404(User_Reg, uid=uid)
    user.status = True
    user.save()

    # Send activation email
    send_activation_email(user, action='activated')

    return redirect('userauths:user_details_view')  # Redirect back to the user details page
