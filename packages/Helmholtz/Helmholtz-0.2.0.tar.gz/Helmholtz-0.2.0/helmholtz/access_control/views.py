#encoding:utf-8
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect 
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.contrib.auth.forms import PasswordResetForm 
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from helmholtz.access_control.decorators import permission_denied
from helmholtz.access_control.models import User
from helmholtz.access_control.forms import LoginForm
from helmholtz.storage.models import File

"""
This module provides :

(i) login and logout facilities
(ii) the ability to download a file
"""
        
def login_session(request, template_name='registration/login.html', form_template=None):
    """
    Extend the login generic view :
    
    (i) launch the authentication if the user doesn't request a reset password
    (ii) else send an email describing this reset procedure.
    """     
    is_login = bool(request.POST.get('Ok', None))
    if request.method == 'GET' or is_login :
        return login(request, template_name, authentication_form=LoginForm)
    else :
        # send a unique link to reset the user password
        login_form = LoginForm(data=request.POST)
        login_form.is_valid()
        if login_form.is_valid() :
            username = request.POST.get('username', None)
            user = User.objects.get(username=username)
            email = user.email
            form = PasswordResetForm({'email':email})
            if form.is_valid() :
                form.save(use_https=settings.SESSION_COOKIE_SECURE)
                redirection = reverse('home')
                return HttpResponseRedirect(redirection) 
        return render_to_response(template_name, RequestContext(request, {'form':login_form}))

@login_required
def download_file(request, file_id) :
    """
    Download the file corresponding to the specified id 
    if the user has a ``can_download`` permission on it 
    else return the permission denied page.
    """
    proxy_user = User.objects.get(pk=request.user.pk)
    format = request.GET.get('format')
    file = File.objects.get(pk=int(file_id))
    if not proxy_user.can_view(file) :
        return permission_denied(request) 
    path = file.get_path(format)
    data = open(path, "rb")
    response = HttpResponse(content=data, mimetype="application/octet-stream")
    response['Content-Disposition'] = "attachment; filename = %s.%s" % (file.name, format)
    return response
