#encoding:utf-8
import httplib, base64
from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from helmholtz.access_control.models import User, Group

"""
The login facility is provided with a
specific :class:`RemoteAuthenticationBackend`
remote authentication backend. 
"""

class RemoteAuthenticationBackend(RemoteUserBackend):
    """
    A backend to identify a member that could be identified
    by several remote server. When identified, a user and its
    password are stored into the database.
    """
    
    def authenticate(self, **credentials):
        # init username and password
        username = credentials['username']
        if not username :
            return
        password = credentials['password']
        
        # encode username and password
        raw = "%s:%s" % (username, password)
        auth = base64.b64encode(raw).strip()
        auth_header = {'Authorization':'Basic %s' % (auth)}
        
        # authentification against all specified remote servers
        for kwargs in settings.AUTHENTICATION_SERVERS :
            # used httplib class depends of the specified protocol
            assert kwargs['protocol'] in ['http', 'https']
            _cls = getattr(httplib, '%sConnection' % (kwargs['protocol'].upper()))
            server = _cls(kwargs['host'])
            
            # send the request to the server and get the response
            server.request(kwargs['type'], kwargs['auth_root'], {}, auth_header)
            response = server.getresponse()
            is_authenticated = (response.reason != "Authorization Required")
            
            # store and configure user
            user = None
            username = self.clean_username(username)
            if is_authenticated :
                user, created = User.objects.get_or_create(username=username)
                if created:
                    self.configure_user(user, password, kwargs['group'])
                break
        return user
    
    def configure_user(self, user, password, grp_name):
        """`
        Configure user group and password.
        """
        group, created = Group.objects.get_or_create(name=grp_name)
        user.first_name = user.username.title()
        user.last_name = grp_name.title()
        user.set_password(password)
        user.save()
        user.groups.add(group)
