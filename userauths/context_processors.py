from django.contrib.sites.shortcuts import get_current_site

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
