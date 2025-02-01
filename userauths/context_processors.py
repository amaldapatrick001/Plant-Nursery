from django.contrib.sites.shortcuts import get_current_site
from .models import Expert, Login, User_Reg
import logging

logger = logging.getLogger(__name__)

def site_context(request):
    current_site = get_current_site(request)
    return {
        'domain': current_site.domain,
        'protocol': 'https' if request.is_secure() else 'http',
    }

def site_info(request):
    return {
        'site_name': 'My Site',
        'site_description': 'This is a description of my site.',
    }

def expert_profile(request):
    """Add expert profile information to the request context if user is logged in."""
    if 'user_id' in request.session:
        try:
            user_id = request.session['user_id']
            login = Login.objects.get(login_id=user_id)
            expert = Expert.objects.select_related('user').get(login=login)
            
            # Debug logging
            logger.debug(f"Expert found: {expert}")
            logger.debug(f"Profile picture: {expert.profile_picture}")
            logger.debug(f"Profile picture URL: {expert.profile_picture.url if expert.profile_picture else 'No picture'}")
            
            return {'user_expert': expert}
        except (Login.DoesNotExist, Expert.DoesNotExist) as e:
            logger.error(f"Error fetching expert profile: {str(e)}")
            return {'user_expert': None}
    return {'user_expert': None}
