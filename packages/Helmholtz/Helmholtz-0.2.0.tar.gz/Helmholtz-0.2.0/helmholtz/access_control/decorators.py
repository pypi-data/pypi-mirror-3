#encoding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from helmholtz.access_control.models import UnderAccessControlEntity

def permission_denied(request, *args, **kwargs):
    """Return the permission_denied page."""
    return render_to_response('permission_denied.html', context_instance=RequestContext(request))

def under_access_control(view_func):
    """Check if an entity is under access control."""
    def modified_function(cls, *args, **kwargs):
        if UnderAccessControlEntity.objects.is_registered(cls):
            return view_func(cls, *args, **kwargs)
        else:
            raise Exception("class %s%s is not under access control" % (cls.__class__.__module__, cls.__class__.__name__))       
    modified_function.__doc__ = view_func.__doc__
    return modified_function

def group_membership_required(*group_list):
    """
    Check if a user belongs to one of the groups supplied in
    group_list, and returns the permission_denied view otherwise.
    """
    def modified_view(view_func):
        def deny_permission_if_not_in_group(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_list).count():
                return view_func(request, *args, **kwargs)
            else:
                return permission_denied(request)       
        deny_permission_if_not_in_group.__doc__ = view_func.__doc__
        return deny_permission_if_not_in_group
    return modified_view
