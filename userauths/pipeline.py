from django.utils import timezone
from .models import User_Reg, Login, UserType
import logging

logger = logging.getLogger(__name__)

def create_or_get_user_from_google(details):
    """Helper function to create or get user from Google details"""
    email = details.get('email')
    first_name = details.get('first_name', '')
    last_name = details.get('last_name', '')

    try:
        # Try to get existing login
        login_user = Login.objects.get(email=email)
        login_user.is_google_user = True
        login_user.save()
        return login_user.uid, login_user

    except Login.DoesNotExist:
        # Create new user
        try:
            customer_type = UserType.objects.get(utid=2)  # Get Customer type
            user_reg = User_Reg.objects.create(
                first_name=first_name,
                last_name=last_name,
                phoneno='',  # Can be updated later
                user_type=customer_type,
                status=True
            )

            # Create login entry
            login_user = Login.objects.create(
                uid=user_reg,
                email=email,
                password='',  # No password for Google users
                status=True,
                is_google_user=True
            )
            return user_reg, login_user

        except Exception as e:
            logger.error(f"Error creating user from Google: {str(e)}")
            raise