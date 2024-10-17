import logging
from .models import User_Reg, Login, UserType
from django.utils import timezone

logger = logging.getLogger(__name__)

def custom_create_user(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email')
    first_name = details.get('first_name')
    last_name = details.get('last_name')

    if email is None:
        return None  # No email returned

    try:
        login_user = Login.objects.get(email=email)
        return {'user': login_user.uid}  # Return the corresponding User_Reg instance
    except Login.DoesNotExist:
        user_reg = User_Reg.objects.create(
            first_name=first_name,
            last_name=last_name,
            phoneno='',  # Default if no phone number from Google
            user_type=UserType.objects.get(usertype='Customer')
        )
        Login.objects.create(
            uid=user_reg,
            email=email,
            password='',  # Password not required for Google login
            status=True
        )

        return {'user': user_reg}  # Return the User_Reg instance

from django.utils import timezone
from .models import Login

def custom_login_user(strategy, user, *args, **kwargs):
    if isinstance(user, User_Reg):
        logger.debug(f"Logging in user: {user.uid}")
        login_user = Login.objects.get(uid=user)

        # Update last_login to the current time
        login_user.last_login = timezone.now()
        login_user.login_count += 1
        login_user.save()

        # Set the session
        strategy.session_set('user_id', user.uid)
        return {'user': user}
    else:
        logger.error("Provided user is not a User_Reg instance")
        return {'user': None}
