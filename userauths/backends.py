
from social_core.backends.google import GoogleOAuth2
from userauths.models import User_Reg, Login

class CustomGoogleOAuth2(GoogleOAuth2):
    def get_user_details(self, response):
        """Return user details from Google account"""
        return {
            'email': response.get('email', ''),
            'first_name': response.get('given_name', ''),
            'last_name': response.get('family_name', '')
        }

    def get_user(self, user_id):
        """Get the user based on the ID (assumes user_id is linked to Login model)"""
        try:
            return Login.objects.get(pk=user_id).uid  # Get the corresponding User_Reg instance
        except Login.DoesNotExist:
            return None