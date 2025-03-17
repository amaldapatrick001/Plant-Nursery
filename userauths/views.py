import json
import logging
import random
import string
logger = logging.getLogger(__name__)

from django.http import BadHeaderError, JsonResponse
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

from .models import Login, User_Reg, UserType, Expert, DeliveryPersonnel
from django.views.decorators.cache import cache_control
from .forms import AddExpertForm, ExpertPasswordChangeForm, RegistrationForm, CustomPasswordResetForm, CustomSetPasswordForm, ExpertProfileUpdateForm, DeliveryProfileUpdateForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .models import Login, UserType

from django.core.mail import send_mail
from django.conf import settings

from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.db import transaction

from google_auth_oauthlib.flow import Flow
from django.urls import reverse

from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expert, User_Reg, Login
import logging

from django.db.models import Avg, Count, Sum, Q
from decimal import Decimal
from products.models import Batch, Category, Product
#from products.views import get_collaborative_recommendations
from purchase.models import Review
import traceback
from expert_QA_session.models import Expert  # Add this import

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']

            # Check if email already exists in the Login table
            if Login.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please use a different email address.')
                return render(request, 'userauths/register.html', {'form': form, 'status': 'error'})

            # Save the user
            user = form.save(commit=False)
            try:
                user.user_type = UserType.objects.get(utid=2)  # Assuming UserType is correctly set
            except UserType.DoesNotExist:
                messages.error(request, 'User type not found. Please try again later.')
                return render(request, 'userauths/register.html', {'form': form, 'status': 'error'})

            user.status = True
            user.save()

            # Create the Login entry with the hashed password
            user_login = Login.objects.create(
                uid=user,
                email=email,
                login_count=0,
                status=False  # Initially not logged in
            )

            # Set the password using the model's method (automatically hashes the password)
            user_login.set_password(password1)
            user_login.save()

            # Send registration email
            send_registration_email(user_login)

            # Success message and redirect to the same page with success status
            messages.success(request, 'Registration successful. You can now log in.')
            return render(request, 'userauths/register.html', {'form': form, 'status': 'success'})
        else:
            # In case of form errors, render the form with error messages
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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control
from purchase.models import Order

import logging
from django.utils.timezone import now

# Set up logging
logger = logging.getLogger(__name__)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_login = Login.objects.get(email=email)

            if user_login.status:
                error_message = 'This account is already logged in from another session.'
                messages.error(request, error_message)
                logger.error(f"[{now()}] Login Error: {error_message} (Email: {email})")
                return redirect('userauths:login')

            if user_login.check_password(password):
                # Update login status and timestamps
                user_login.status = True
                user_login.last_login = timezone.now()
                user_login.login_count += 1
                user_login.save()

                # Set session data
                request.session['user_id'] = user_login.login_id
                request.session['user_first_name'] = user_login.uid.first_name
                request.session['user_last_name'] = user_login.uid.last_name
                request.session['email'] = user_login.email
                request.session['is_authenticated'] = True

                # Fetch user's orders
                user_orders = Order.objects.filter(user_id=request.session['user_id'])
                request.session['user_orders'] = [order.id for order in user_orders] if user_orders.exists() else []

                # Redirect based on user type
                user_type = user_login.uid.user_type_id
                user_type_redirects = {
                    1: 'userauths:adminindex',
                    2: 'userauths:index',
                    3: 'userauths:delivery_dashboard',
                    4: 'userauths:expert_dashboard'
                }

                success_message = f"User {user_login.uid.first_name} {user_login.uid.last_name} logged in successfully."
                logger.info(f"[{now()}] Login Success: {success_message} (Email: {email})")
                return redirect(user_type_redirects.get(user_type, 'userauths:login'))
            else:
                error_message = 'Incorrect password.'
                messages.error(request, error_message)
                logger.warning(f"[{now()}] Login Error: {error_message} (Email: {email})")

        except Login.DoesNotExist:
            error_message = 'No account found with this email.'
            messages.error(request, error_message)
            logger.warning(f"[{now()}] Login Error: {error_message} (Email: {email})")

    return render(request, 'userauths/login.html')



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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            experts = Expert.objects.select_related('user').all()
            
            context.update({
                'experts': experts,
                'has_experts': experts.exists(),
                'debug': True,
                'debug_info': {
                    'total_experts': experts.count(),
                    'expert_list': [
                        {
                            'id': e.expert_id,
                            'name': f"{e.user.first_name} {e.user.last_name}",
                            'expertise': e.expertise_area
                        } for e in experts
                    ]
                }
            })

        except Exception as e:
            context.update({
                'experts': [],
                'has_experts': False,
                'debug': True,
                'error_message': str(e)
            })
        
        # Add recommended products based on authentication status
        if self.request.user.is_authenticated:
            recommended_products = self.get_recommended_products()
        else:
            recommended_products = self.get_popular_products()
        
        # Calculate discounted price and get average rating for each product
        for batch in recommended_products:
            if batch.discount:
                discount_amount = (batch.price * Decimal(batch.discount)) / 100
                batch.discounted_price = batch.price - discount_amount
            
            # Get average rating from the product's reviews using the correct related name
            reviews = Review.objects.filter(product=batch.product)
            if reviews.exists():
                batch.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            else:
                batch.avg_rating = None
            
        context['recommended_products'] = recommended_products
        return context
    
    def get_recommended_products(self):
        """
        Get personalized recommendations for authenticated users.
        """
        return (Batch.objects
                .select_related('product')
                .filter(status=True)
                .order_by('-created_on')[:4])
    
    def get_popular_products(self):
        """
        Get popular products for non-authenticated users
        """
        return (Batch.objects
                .select_related('product')
                .filter(status=True)
                .order_by('-stock_quantity')[:4])



    

    
from django.db.models import Count
from django.shortcuts import render
from .models import User_Reg # Assuming these are in the current app
from products.models import Product  # Import Product from the 'product' app


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class adminindex(TemplateView):
    
    template_name = "core/adminindex.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Count users with uid = 2
        context['user_count_with_uid_2'] = User_Reg.objects.filter(user_type=2).count()
        
        # Get the total count of users (with fallback to 0 if no data exists)
        context['order_count'] = Order.objects.count() if Order.objects.exists() else 0
        
        # Get the total count of products (assuming Product model is defined)
        context['product_count'] = Product.objects.count() if Product.objects.exists() else 0
        
        return context



def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Login.objects.get(email=email)
                
                # Create token manually
                uid = urlsafe_base64_encode(force_bytes(user.login_id))
                token = default_token_generator.make_token(user)
                
                # Build reset URL
                current_site = get_current_site(request)
                reset_url = f"{request.scheme}://{current_site.domain}/userauths/reset/{uid}/{token}/"
                
                # Send email
                subject = "Password Reset Request"
                email_body = render_to_string('userauths/password_reset_email.html', {
                    'email': user.email,
                    'reset_url': reset_url,
                    'site_name': current_site.name,
                    'protocol': request.scheme,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                })
                
                send_mail(
                    subject,
                    email_body,
                    'noreply@enchantededen.com',
                    [user.email],
                    fail_silently=False,
                )
                
                messages.success(request, "Password reset instructions have been sent to your email.")
                return redirect('userauths:password_reset_done')
                
            except Login.DoesNotExist:
                messages.error(request, "No account found with this email address.")
                
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'userauths/password_reset_form.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Login.objects.get(login_id=uid)
    except (TypeError, ValueError, OverflowError, Login.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully!")
                return redirect('userauths:password_reset_complete')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'userauths/password_reset_confirm.html', {
            'form': form,
            'validlink': True
        })
    else:
        return render(request, 'userauths/password_reset_invalid.html')






    
# myproject/userauths/views.py
from django.shortcuts import render, get_object_or_404
from .models import User_Reg, UserType, Login

def user_details(request):
    
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')
    # Fetch users with user_type 2 (customers) and related login and usertype data
    users = User_Reg.objects.filter(user_type__utid=2).select_related('user_type').prefetch_related('login_set')

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
    
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')
    # Fetch active and deleted users with user_type=2 (customers) and related login data
    active_users = User_Reg.objects.filter(status=True, user_type__utid=2).prefetch_related('login_set')
    deleted_users = User_Reg.objects.filter(status=False, user_type__utid=2).prefetch_related('login_set')

    # Prepare user login info for both active and deleted users
    logins = Login.objects.filter(uid__user_type__utid=2)

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
    
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')
    # Soft delete user by setting status to False
    user = get_object_or_404(User_Reg, uid=uid)
    user.status = False
    user.save()

    # Send deactivation email
    send_activation_email(user, action='deactivated')

    return redirect('userauths:user_details_view')  # Redirect back to the user details page

def undo_delete_view(request, uid):
    
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')
    # Restore user by setting status to True
    user = get_object_or_404(User_Reg, uid=uid)
    user.status = True
    user.save()

    # Send activation email
    send_activation_email(user, action='activated')

    return redirect('userauths:user_details_view')  # Redirect back to the user details page




from .models import User_Reg

def get_logged_in_user(request):
    if 'user_id' in request.session:
        return User_Reg.objects.get(uid=request.session['user_id'])
    return None
from django.shortcuts import redirect

def custom_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login_page')  # Redirect to your login page

def google_login(request):
    """Initiates the Google OAuth2 login flow"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
                }
            },
            # Update scopes to match exactly what Google is returning
            scopes=[
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid'
            ]
        )
        
        flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store state in session
        request.session['google_oauth_state'] = state
        return redirect(authorization_url)
        
    except Exception as e:
        logger.error(f"Error initiating Google login: {str(e)}")
        messages.error(request, 'Failed to initiate Google login. Please try again.')
        return redirect('userauths:login')

def google_callback(request):
    """Handles the Google OAuth2 callback"""
    try:
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid'
            ]
        )
        
        flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        
        # Fetch token
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get user info with clock skew tolerance
        credentials = flow.credentials
        google_request = requests.Request()
        user_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_request,
            settings.GOOGLE_OAUTH_CLIENT_ID,
            clock_skew_in_seconds=300  # Add 5 minutes tolerance
        )

        email = user_info.get('email')
        if not email:
            messages.error(request, 'Email not provided by Google')
            return redirect('userauths:login')

        # Create or get user
        with transaction.atomic():
            try:
                login_user = Login.objects.get(email=email)
                user_reg = login_user.uid
            except Login.DoesNotExist:
                # Create new user if not exists
                customer_type = UserType.objects.get(utid=2)
                user_reg = User_Reg.objects.create(
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    phoneno='',
                    user_type=customer_type,
                    status=True
                )
                login_user = Login.objects.create(
                    uid=user_reg,
                    email=email,
                    status=True,
                    is_google_user=True
                )

            # Update login status and timestamps
            login_user.status = True
            login_user.last_login = timezone.now()
            login_user.login_count += 1
            login_user.save()

            # Set session data
            request.session['user_id'] = login_user.login_id
            request.session['user_first_name'] = user_reg.first_name
            request.session['user_last_name'] = user_reg.last_name
            request.session['email'] = email
            request.session['is_authenticated'] = True
            request.session.modified = True

            # Get user type and redirect accordingly
            user_type = user_reg.user_type.utid
            user_type_redirects = {
                1: 'userauths:adminindex',
                2: 'userauths:index',
                3: 'userauths:delivery_dashboard',
                
                4: 'userauths:update_expert_profile'
            }

            messages.success(request, f'Welcome {user_reg.first_name}!')
            return redirect(user_type_redirects.get(user_type, 'userauths:index'))

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        messages.error(request, str(ve))
        return redirect('userauths:login')
    except Exception as e:
        logger.error(f"Google authentication error: {str(e)}")
        messages.error(request, 'Authentication failed. Please try again.')
        return redirect('userauths:login')

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AddExpertForm
from django.core.mail import send_mail, BadHeaderError
from .models import User_Reg, UserType, Login, Expert
import random
import string
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

def add_expert(request):
    if request.method == 'POST':
        form = AddExpertForm(request.POST)
        
        if form.is_valid():
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            # Validate the email format
            try:
                EmailValidator()(email)  # Check if the email is valid
            except ValidationError:
                messages.error(request, 'Invalid email format! Please enter a valid email address.')
                return render(request, 'userauths/add_expert.html', {'form': form})  # Stay on the same page

            # Check if the email already exists in the Login model
            if Login.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists!')
                return render(request, 'userauths/add_expert.html', {'form': form})  # Stay on the same page

            try:
                # Get the UserType with utid = 4 (expert)
                user_type = UserType.objects.get(utid=4)  # Ensure that 'expert' has utid = 4
                
                user = User_Reg.objects.create(
                    first_name=fname,
                    last_name=lname,
                    phoneno=phone,
                    user_type=user_type
                )

                # Generate a random password
                raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                # Create the Login entry with a hashed password
                login = Login.objects.create(
                    uid=user,
                    email=email
                )
                login.set_password(raw_password)  # Hash the password
                login.save()

                # Send login credentials via email
                subject = "Welcome to Expert Platform"
                message = f"""
                Hello {fname},

                You have been registered as an expert on our platform. Please use the following credentials to log in:
                Email: {email}
                Password: {raw_password}

                Login here: http://yourwebsite.com/login/

                Thank you!
                """
                send_mail(subject, message, 'admin@yourwebsite.com', [email], fail_silently=False)

                # Create expert entry with default values
                Expert.objects.create(user=user, login=login)

                messages.success(request, 'Expert added successfully! Login credentials have been sent.')
                return redirect('userauths:add_expert')  # Redirect to the same page after successful form submission

            except BadHeaderError:
                messages.error(request, 'Invalid email header detected.')
                return render(request, 'userauths/add_expert.html', {'form': form})  # Stay on the same page
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                return render(request, 'userauths/add_expert.html', {'form': form})  # Stay on the same page

    else:
        form = AddExpertForm()

    return render(request, 'userauths/add_expert.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Expert
from .forms import ExpertProfileUpdateForm
from .models import User_Reg  # Assuming you have a User_Reg model to check for logged-in user

def update_expert_profile(request):
    if 'user_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    try:
        # First get the Login object using login_id from session
        login_user = Login.objects.get(login_id=request.session['user_id'])
        # Then get the User_Reg through the uid field
        user = login_user.uid
        expert = get_object_or_404(Expert, user=user)

        if request.method == 'POST':
            form = ExpertProfileUpdateForm(request.POST, request.FILES, instance=expert)
            if form.is_valid():
                expert = form.save(commit=False)
                
                # Handle profile picture
                if 'profile_picture' in request.FILES:
                    expert.profile_picture = request.FILES['profile_picture']
                
                # Handle availability schedule
                schedule_data = request.POST.get('availability_schedule')
                if schedule_data:
                    try:
                        expert.availability_schedule = json.loads(schedule_data)
                    except json.JSONDecodeError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid schedule format'
                        }, status=400)
                
                expert.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profile updated successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please correct the following errors:',
                    'errors': {field: errors[0] for field, errors in form.errors.items()}
                }, status=400)
        else:
            form = ExpertProfileUpdateForm(instance=expert)
            return render(request, 'userauths/eupdate_profile.html', {
                'form': form,
                'expert': expert
            })

    except Login.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Expert.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Expert profile not found'
        }, status=404)
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

from django.core.mail import send_mail
from django.conf import settings

def echange_password(request):
    # Check if the user is logged in using the session
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to change your password.')
        return redirect('userauths:login')  # Redirect to login page if not authenticated

    user_id = request.session.get('user_id')

    try:
        # Fetch the logged-in user's Login object
        user_login = Login.objects.get(pk=user_id)
    except Login.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('userauths:login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the current password
        if not user_login.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")
            return render(request, 'userauths/echange_password.html', {'status': 'error'})

        # Ensure the new password matches the confirm password
        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return render(request, 'userauths/echange_password.html', {'status': 'error'})

        # Update the password
        user_login.set_password(new_password)  # Hash the new password
        user_login.save()

        # Optionally send an email notification about the password change
        send_password_change_email(user_login)

        # Success message and redirect
        messages.success(request, "Your password has been changed successfully.")
        return render(request, 'userauths/echange_password.html', {'status': 'success'})

    # Render the password change form
    return render(request, 'userauths/echange_password.html', {'status': 'form'})

def send_password_change_email(user_login):
    """Send an email notification upon successful password change."""
    subject = "Your Password Has Been Changed"
    message = (
        f"Dear {user_login.uid.first_name},\n\n"
        "This is a confirmation that your password has been successfully changed.\n\n"
        "If you did not request this change, please contact our support team immediately.\n\n"
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


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DeliveryPersonnelRegistrationForm
from .models import User_Reg, Login, DeliveryPersonnel, UserType
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
import traceback

def register_delivery_personnel(request):
    if request.method == 'POST':
        form = DeliveryPersonnelRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                
                # Check if email exists
                if Login.objects.filter(email=email).exists():
                    logger.warning(f"Registration attempt with existing email: {email}")
                    messages.error(request, 'This email is already registered.')
                    return render(request, 'userauths/register_delivery_personnel.html', {'form': form})
                
                try:
                    # Create User_Reg
                    user_type = UserType.objects.get(usertype='Delivery')
                except UserType.DoesNotExist:
                    logger.error("UserType 'Delivery' not found in database")
                    messages.error(request, 'System configuration error: Delivery user type not found')
                    return render(request, 'userauths/register_delivery_personnel.html', {'form': form})

                try:
                    # Create User_Reg
                    user = User_Reg.objects.create(
                        user_type=user_type,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
                    logger.info(f"Created User_Reg record for {email}")

                    # Generate and create login credentials
                    password = get_random_string(length=12)
                    login = Login.objects.create(
                        uid=user,
                        email=email
                    )
                    login.set_password(password)
                    login.save()
                    logger.info(f"Created Login record for {email}")

                    # Create DeliveryPersonnel
                    delivery_personnel = DeliveryPersonnel.objects.create(
                        user=user,
                        area_of_delivery=form.cleaned_data['area_of_delivery'],
                        status=form.cleaned_data['status'],
                        max_daily_orders=form.cleaned_data['max_daily_orders'],
                        current_latitude=form.cleaned_data['latitude'],
                        current_longitude=form.cleaned_data['longitude']
                    )
                    logger.info(f"Created DeliveryPersonnel record for {email}")

                    try:
                        # Send email with credentials
                        send_mail(
                            'Your Delivery Personnel Account Credentials',
                            f'Email: {email}\nPassword: {password}\n\nPlease change your password after first login.',
                            'noreply@plantnursery.com',
                            [email],
                            fail_silently=False,
                        )
                        logger.info(f"Sent credentials email to {email}")
                    except Exception as e:
                        logger.error(f"Failed to send email to {email}: {str(e)}")
                        messages.warning(request, 'Account created but failed to send email with credentials.')
                        # Continue execution since account was created

                    messages.success(request, 'Delivery Personnel registered successfully. Credentials sent to email.')
                    return redirect('userauths:delivery_personnel_list')  # or appropriate URL

                except Exception as e:
                    # If any error occurs after user creation, cleanup partial records
                    if 'user' in locals():
                        logger.error(f"Cleaning up partial registration for {email}")
                        user.delete()
                    
                    logger.error(f"Registration failed for {email}: {str(e)}\n{traceback.format_exc()}")
                    messages.error(request, 'Registration failed. Please try again.')
                    return render(request, 'userauths/register_delivery_personnel.html', {'form': form})

            except Exception as e:
                logger.error(f"Unexpected error during registration: {str(e)}\n{traceback.format_exc()}")
                messages.error(request, 'An unexpected error occurred. Please try again.')
                return render(request, 'userauths/register_delivery_personnel.html', {'form': form})
        else:
            logger.warning(f"Invalid form submission: {form.errors}")
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = DeliveryPersonnelRegistrationForm()

    return render(request, 'userauths/register_delivery_personnel.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import DeliveryPersonnel
from .forms import DeliveryPersonnelForm

def delivery_personnel_list(request):
    """Display all DeliveryPersonnel."""
    delivery_personnel_list = DeliveryPersonnel.objects.select_related('user').all()
    return render(request, 'userauths/delivery_personnel_list.html', {'delivery_personnel_list': delivery_personnel_list})

def edit_delivery_personnel(request, delivery_id):
    """Edit the details of a DeliveryPersonnel."""
    delivery_personnel = get_object_or_404(DeliveryPersonnel, pk=delivery_id)
    if request.method == 'POST':
        form = DeliveryPersonnelForm(request.POST, instance=delivery_personnel)
        if form.is_valid():
            form.save()
            return redirect('userauths:delivery_personnel_list')
    else:
        form = DeliveryPersonnelForm(instance=delivery_personnel)
    return render(request, 'userauths/edit_delivery_personnel.html', {'form': form})

def delete_delivery_personnel(request, delivery_id):
    """Mark a DeliveryPersonnel as inactive."""
    delivery_personnel = get_object_or_404(DeliveryPersonnel, pk=delivery_id)
    delivery_personnel.user.status = False  # Turn off registration status
    delivery_personnel.user.save()
    return redirect('userauths:delivery_personnel_list')

def restore_delivery_personnel(request, delivery_id):
    """Mark a DeliveryPersonnel as active."""
    delivery_personnel = get_object_or_404(DeliveryPersonnel, pk=delivery_id)
    delivery_personnel.user.status = True  # Turn on registration status
    delivery_personnel.user.save()
    return redirect('userauths:delivery_personnel_list')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delivery_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        # Get the login object first
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid  # Get the User_Reg object
        
        # Get delivery personnel details
        delivery_personnel = get_object_or_404(DeliveryPersonnel, user=user)
        
        context = {
            'delivery_personnel': delivery_personnel,
            'user': user,
        }
        return render(request, 'userauths/delivery_dashboard.html', context)
    except (Login.DoesNotExist, User_Reg.DoesNotExist) as e:
        logger.error(f"Error accessing delivery dashboard: {str(e)}")
        return redirect('userauths:login')
    except DeliveryPersonnel.DoesNotExist:
        logger.error(f"User {user.uid} is not registered as delivery personnel")
        return redirect('userauths:login')




def expert_dashboard(request):
    """
    View for the expert's dashboard. Shows their profile, stats, and quick actions.
    Uses session-based authentication.
    """
    if 'user_id' not in request.session:
        return redirect('userauths:login')

    try:
        # Get the login object first
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user = login_user.uid  # Get the User_Reg object
        
        # Get expert details
        expert = get_object_or_404(Expert, user=user)
        
        context = {
            'expert': expert,
            'phone': user.phoneno,  # From User_Reg model
            'email': login_user.email,  # From Login model
            'page_title': 'Expert Dashboard',
            'active_page': 'dashboard',
        }
        
        return render(request, 'userauths/expert_dashboard.html', context)
    
    except Login.DoesNotExist:
        logger.error(f"Login object not found for user_id: {request.session['user_id']}")
        return redirect('userauths:login')
    except Expert.DoesNotExist:
        logger.error(f"Expert profile not found for user: {user.uid}")
        return redirect('userauths:login')
    except Exception as e:
        logger.error(f"Unexpected error in expert dashboard: {str(e)}")
        return redirect('userauths:login')

def toggle_expert_availability(request):
    """
    AJAX view to toggle expert's availability status.
    Uses session-based authentication.
    """
    if 'user_id' not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Not authenticated'
        }, status=401)

    if request.method == 'POST':
        try:
            login_user = Login.objects.get(login_id=request.session['user_id'])
            user = login_user.uid
            expert = get_object_or_404(Expert, user=user)
            
            new_status = 'unavailable' if expert.availability_status == 'available' else 'available'
            expert.availability_status = new_status
            expert.save()
            
            return JsonResponse({
                'status': 'success',
                'new_status': new_status
            })
        except Login.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Login not found'
            }, status=404)
        except Expert.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Expert profile not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error toggling expert availability: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An unexpected error occurred'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)





from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Expert, User_Reg, Login
from django.utils import timezone

def expert_details(request, expert_id):
    """View for fetching expert details for modal display"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    try:
        # Use select_related to fetch related data efficiently
        expert = Expert.objects.select_related('user', 'login').get(expert_id=expert_id)
        
        if not expert:
            return JsonResponse({'error': 'Expert not found'}, status=404)
            
        context = {
            'expert': expert,
            'user': expert.user,
            'login': expert.login,
            'last_login': expert.login.last_login,
            'consultation_history': {
                'total': expert.consultation_count,
                'rating': expert.rating,
                'reviews': expert.total_reviews
            }
        }
        
        return render(request, 'userauths/amanage_experts.html', context)
    except Expert.DoesNotExist:
        logger.warning(f"Expert with ID {expert_id} not found")
        return JsonResponse({'error': 'Expert not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching expert details: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def toggle_expert_status(request, expert_id):
    """Toggle expert's active status"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        expert = Expert.objects.select_related('user').get(expert_id=expert_id)
        user = expert.user
        
        # Toggle status
        user.status = not user.status
        user.save()
        
        # Log the status change
        action = "activated" if user.status else "deactivated"
        logger.info(f"Expert {expert_id} {action} by admin {request.session.get('user_id')}")
        
        return JsonResponse({
            'status': 'success',
            'new_status': 'active' if user.status else 'inactive',
            'message': f'Expert successfully {action}'
        })
    except Expert.DoesNotExist:
        logger.warning(f"Expert with ID {expert_id} not found")
        return JsonResponse({
            'status': 'error',
            'message': 'Expert not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error toggling expert status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while updating expert status'
        }, status=500)

def manage_experts(request):
    """View for managing experts"""
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('userauths:login')
        
    try:
        # Get all experts with related data
        experts = Expert.objects.select_related('user', 'login').all()
        
        # Calculate statistics
        total_experts = experts.count()
        active_experts = sum(1 for expert in experts if expert.user.status)
        inactive_experts = total_experts - active_experts
        
        # Calculate average rating safely
        total_rating = sum(expert.rating for expert in experts if expert.rating is not None)
        avg_rating = total_rating / total_experts if total_experts > 0 else 0.0

        context = {
            'experts': experts,
            'total_experts': total_experts,
            'active_experts': active_experts,
            'inactive_experts': inactive_experts,
            'avg_rating': round(avg_rating, 1)
        }
        
        return render(request, 'userauths/amanage_experts.html', context)
    except Exception as e:
        logger.error(f"Error in manage_experts view: {str(e)}")
        messages.error(request, 'An error occurred while loading expert management.')
        return redirect('userauths:dashboard')

def view_all_experts(request):
    try:
        # Get all experts with related data
        experts = Expert.objects.select_related('user', 'login').all()
        
        # Calculate statistics
        stats = {
            'total_experts': experts.count(),
            'active_experts': experts.filter(user__status=True).count(),
            'avg_rating': experts.aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_consultations': experts.aggregate(total=Sum('consultation_count'))['total'] or 0
        }
        
        context = {
            'experts': experts,
            'stats': stats,
            'page_title': 'Our Plant Care Experts'
        }
        
        return render(request, 'core/index.html', context)
        
    except Exception as e:
        messages.error(request, 'Error loading experts. Please try again later.')
        return render(request, 'core/index.html', {'error': str(e)})

def update_delivery_profile(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to update your profile.')
        return redirect('userauths:login')

    try:
        login_user = Login.objects.get(login_id=request.session['user_id'])
        user_reg = login_user.uid
        delivery_profile = DeliveryPersonnel.objects.get(user=user_reg)
        
        if request.method == 'POST':
            # Update User_Reg fields
            user_reg.first_name = request.POST.get('first_name')
            user_reg.last_name = request.POST.get('last_name')
            user_reg.phoneno = request.POST.get('phone_number')
            user_reg.save()
            
            # Update DeliveryPersonnel fields
            delivery_profile.vehicle_number = request.POST.get('vehicle_number')
            delivery_profile.status = request.POST.get('status')
            
            if 'profile_picture' in request.FILES:
                delivery_profile.profile_picture = request.FILES['profile_picture']
            
            delivery_profile.save()
            
            # Update session data
            request.session['user_first_name'] = request.POST.get('first_name')
            request.session['user_last_name'] = request.POST.get('last_name')
            request.session.modified = True
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('userauths:update_delivery_profile')

        context = {
            'delivery_profile': delivery_profile,
            'user_reg': user_reg,
            'login': login_user
        }
        return render(request, 'userauths/update_delivery_profile.html', context)
        
    except Login.DoesNotExist:
        messages.error(request, 'User account not found.')
        return redirect('userauths:login')
    except DeliveryPersonnel.DoesNotExist:
        messages.error(request, 'Delivery personnel profile not found.')
        return redirect('userauths:login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('userauths:login')

def change_delivery_password(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to change password.')
        return redirect('userauths:login')
        
    try:
        login_user = Login.objects.get(login_id=request.session['user_id'])
        
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            
            # Verify old password
            if not check_password(old_password, login_user.password):
                messages.error(request, 'Current password is incorrect.')
                return render(request, 'userauths/change_delivery_password.html')
            
            # Hash and save new password
            login_user.password = make_password(new_password)
            login_user.save()
            
            messages.success(request, 'Password changed successfully!')
            return redirect('userauths:update_delivery_profile')
            
        return render(request, 'userauths/change_delivery_password.html')
        
    except Login.DoesNotExist:
        messages.error(request, 'User account not found.')
        return redirect('userauths:login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('userauths:login')