#encoding:utf-8
from copy import copy
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib import auth
from helmholtz.access_control.backends import RemoteAuthenticationBackend

def authenticate(**credentials):
    """
    Override the base django.contrib.auth.authenticate.
    When a :class:`RemoteAuthenticationBackend` is detected,
    Launch the authentication against all remote servers
    specified in settings.AUTHENTICATION_SERVERS parameter.
    """
    
    for backend in auth.get_backends():
        try:
            if not isinstance(backend, RemoteAuthenticationBackend) :
                user = backend.authenticate(**credentials)
            else :
                try :
                    # authentificate against all specified remote servers
                    for parameters in settings.AUTHENTICATION_SERVERS :
                        kwargs = copy(parameters)
                        kwargs.update(credentials)
                        user = backend.authenticate(**credentials)
                        if user :
                            break
                except TypeError:
                    # this backend doesn't accept these credentials as arguments. Try the next one.
                    continue
        except TypeError:
            # this backend doesn't accept these credentials as arguments. Try the next one.
            continue
        if user is None:
            continue
        # annotate the user object with the path of the backend.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user

class RemoteAuthenticationMiddleware(object):
    """
    Override the base RemoteUserMiddleware to take from the settings file
    all information needed to contact a remote server for authentication.
    """
    header = "REMOTE_USER"

    def process_request(self, request):
        """
        Override the process_request by using a custom
        authenticate function replacing the django.contrib.auth.authenticate
        in the method body.
        """
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Helmholtz remote authentication middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteAuthenticationMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            return
        if request.user.is_authenticated():
            if request.user.username == self.clean_username(username, request):
                return
        user = authenticate(remote_user=username) # override the auth.authenticate function
        if user:
            request.user = user
            auth.login(request, user)
