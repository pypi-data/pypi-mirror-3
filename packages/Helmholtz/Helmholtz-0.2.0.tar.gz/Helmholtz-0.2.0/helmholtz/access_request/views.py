#encoding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from helmholtz.core.shortcuts import get_form_context
from helmholtz.core.decorators import check_rendered_page
from helmholtz.access_control.decorators import group_membership_required
from helmholtz.access_request.models import AccessRequest
from helmholtz.access_request.forms import PermissionForm
from helmholtz.storage.models import File

"""
This module provides facilities to manage requests to objects. 
"""

@login_required
@group_membership_required('facets', 'incf')
def request_file(request, file_id) :
    """
    Create a new :class:`AccessRequest` from
    request's user and the specified file id.
    """
    file = File.objects.get(pk=int(file_id))
    AccessRequest.objects.request_object(file, request.user)
    return HttpResponseRedirect(request.session['last_page'])

@login_required
def accept_request(request, request_id):
    """
    Accept the request to an object.
    
    NB :
    
    This view is not actually generic. It has been designed
    to simplify accesses and downloads for :class:`File` objects.
    """
    permission = {
        'can_view':True,
        'can_download':True,
    }
    access_request = AccessRequest.objects.get(pk=int(request_id))
    access_request.accept(request.user, **permission)
    return HttpResponseRedirect(request.session['last_page'])

@check_rendered_page
@login_required
def set_access_control(request, request_id, *args, **kwargs):
    """
    Provide a generic way to the owner of an object to customise the
    :class:`UserPermission` instance that should be created right
    after the request validation.
    """
    access_request = AccessRequest.objects.get(pk=int(request_id))
    if request.method == "POST" :
        form = PermissionForm(request.POST)
        if form.is_valid() :
            access_request.accept(request.user, **form.cleaned_data)
            return HttpResponseRedirect(request.session['last_page'])
    else :
        form = PermissionForm()
    context = get_form_context(request, form, "Setup the permission for user %s" % access_request.user.get_full_name())
    context.update(kwargs)
    return render_to_response(context['template'], RequestContext(request, context))

@login_required
def refuse_request(request, request_id):
    """Refuse the request to an object."""
    access_request = AccessRequest.objects.get(pk=int(request_id))
    access_request.refuse(request.user)
    return HttpResponseRedirect(request.session['last_page'])

@login_required
def delete_request(request, request_id):
    """Delete the request to an object."""
    access_request = AccessRequest.objects.get(pk=int(request_id))
    access_request.delete()
    return HttpResponseRedirect(request.session['last_page'])
