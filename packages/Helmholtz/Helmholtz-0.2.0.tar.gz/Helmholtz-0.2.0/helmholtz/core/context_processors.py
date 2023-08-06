from django.conf import settings

def site(request):
    """
    Adds site-related context variables to the context.
    """
    return {
        'SITE_ID':settings.SITE_ID,
        'SITE_DOMAIN':settings.SITE_DOMAIN,
        'SITE_NAME':settings.SITE_NAME,
        'SITE_LOGO':settings.SITE_LOGO,
        'SITE_LOGO_ALT':settings.SITE_LOGO_ALT
    }
