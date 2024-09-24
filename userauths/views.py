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
            user_login = Login.objects.create(
                uid=user,
                email=email,
                login_count=0,
                status=False  # Initially not logged in
            )

            # Set the password using the model's method
            user_login.set_password(password1)

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
        password = request.POST.get('password')

        try:
            user_login = Login.objects.get(email=email)

            if user_login.status:
                messages.error(request, 'This account is already logged in from another session.')
                return redirect('userauths:login')

            if user_login.check_password(password):
                # Successful authentication
                user_login.login()  # This updates last_login, status, and login_count

                # Set user information in session
                request.session['user_id'] = user_login.login_id
                request.session['user_first_name'] = user_login.uid.first_name
                request.session['user_last_name'] = user_login.uid.last_name
                request.session['email'] = user_login.email
                request.session['is_authenticated'] = True

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
                messages.error(request, 'Incorrect password.')
        except Login.DoesNotExist:
            messages.error(request, 'No account found with this email.')

    return render(request, 'userauths/login.html')

from django.contrib.auth import logout as auth_logout

from django.contrib.auth import logout as auth_logout

@transaction.atomic
def logout(request):
    if 'is_authenticated' in request.session and request.session['is_authenticated']:
        try:
            # Fetch the user registration and login entries
            user_reg = User_Reg.objects.get(
                first_name=request.session['user_first_name'], 
                last_name=request.session['user_last_name']
            )
            login_entry = Login.objects.get(uid=user_reg)

            # Debugging: Ensure you are correctly fetching user and login entry
            print(f"Logging out user: {user_reg.first_name} {user_reg.last_name}")

            # Update last_logout and status
            login_entry.logout()  # This sets status to False and updates last_logout
            print(f"Updated last_logout to: {login_entry.last_logout}")

        except User_Reg.DoesNotExist:
            messages.error(request, 'User registration record not found.')
        except Login.DoesNotExist:
            messages.error(request, 'Login entry not found.')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')

        # Now, perform logout and flush the session after updating the login entry
        auth_logout(request)
        request.session.flush()

        # Notify the user
        messages.info(request, 'You have been logged out.')

    return redirect('userauths:index')


from django.views.generic import TemplateView
class IndexView(TemplateView):
    template_name = 'core/index.html'
    
from django.db.models import Count
from django.shortcuts import render
from .models import User_Reg # Assuming these are in the current app
from products.models import Product  # Import Product from the 'product' app

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



from django.shortcuts import render, redirect, get_object_or_404
from .models import User_Reg
from .models import Login  # Import the related Login model

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

def delete_user_view(request, uid):
    # Soft delete user by setting status to False
    user = get_object_or_404(User_Reg, uid=uid)
    user.status = False
    user.save()
    return redirect('userauths:user_details_view')  # Redirect back to the user details page

def undo_delete_view(request, uid):
    # Restore user by setting status to True
    user = get_object_or_404(User_Reg, uid=uid)
    user.status = True
    user.save()
    return redirect('userauths:user_details_view')  # Redirect back to the user details page
