#encoding:utf-8
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User, Group
from helmholtz.core.models import ObjectIndex
from helmholtz.core.shortcuts import get_class
from helmholtz.access_control.models import User as ProxyUser, UnderAccessControlEntity

"""
This module provides a way to users to ask an access request
on an object to its owner. Once the request is sent, the owner
can fix the type of access controls on the requested object for
the requesting users.
"""

class RequestManager(models.Manager):
    """
    Manage :class:`AccessRequest` objects.
    """
    
    def request_object(self, obj, user):
        """
        Create an :class:`AccessRequest` for the specified
        :class:`django.contrib.auth.models.User` and object.
        """
        index = ObjectIndex.objects.register_object(obj)
        request, created = AccessRequest.objects.get_or_create(user=user, index=index)
        return request
    
    def get_permission(self, request):
        """Get the :class:`UserPermission` relative to an :class:`AccessRequest`."""
        up_cls = get_class('access_control', 'userpermission')
        return up_cls.objects.get_permission(request.index.object, request.user)
    
    def get_status_from_user_group(self, obj, user):
        under_access_control = UnderAccessControlEntity.objects.is_registered(obj.__class__)
        return 'all_formats' if not under_access_control or (obj.is_available() and user.is_superuser) else 'not_available'
    
    def download_status_from_request(self, request):
        """Return the download status of an object from a specified :class`AccessRequest`."""
        # use the proxy user to test if 
        # somebody can download the object
        _user = ProxyUser.objects.get(user__pk=request.user.pk)
        status = request.get_state_display()
        if (status == 'accepted') and _user.can_download(request.object) :
            return "all_formats" if request.object.is_available() else "not_available"
        else :
            return status
    
    def download_status(self, obj, user):
        """
        Return the download status for the specified
        object and :class:`django.contrib.auth.models.User`.
        """
        index = ObjectIndex.objects.get_registered_object(obj)
        if not index :
            # index could not exist if an
            # object hasn't got any permissions
            return self.get_status_from_user_group(obj, user) 
        else :
            try :
                request = AccessRequest.objects.get(index=index, user=user)
            except :
                return None
            return self.download_status_from_request(request)

state_type = (('accepted', 'accepted'), ('requested', 'requested'), ('refused', 'refused'))       
class AccessRequest(models.Model):
    """Store access requests to an object."""
    user = models.ForeignKey(User, related_name="requests")
    state = models.CharField(max_length=16, default="requested", choices=state_type)
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    response_by = models.ForeignKey(User, related_name="responses", null=True)
    index = models.ForeignKey(ObjectIndex)
    
    objects = RequestManager()
    
    def _object(self):
        """Return the requested object."""
        return self.index.object
    object = property(_object)
    
    def create_permission(self, **kwargs):
        """Create a :class:`UserPermission` from an :class:`AccessRequest`."""
        up_cls = get_class('access_control', 'userpermission')
        return up_cls.objects.set_permission(self.object, self.user, **kwargs)
    
    def accept(self, user, **kwargs):
        """
        Accept the access request. Cascade the creation of a new :class:`UserPermission`
        based on parameters specified in **kwargs. The decision is done by the
        specified :class:`django.contrib.auth.models.User`.
        """
        #update request
        self.state = 'accepted'
        self.response_by = user
        self.response_date = datetime.now()
        self.save()
        
        #create permission
        permission = self.create_permission(**kwargs)
        return permission
    
    def refuse(self, user):
        """
        Refuse the access request. The decision is done by
        the specified :class`django.contrib.auth.models.User`.
        """
        self.state = 'refused'
        self.response_by = user
        self.response_date = datetime.now()
        self.save()
    
    def get_permission(self):
        """
        Return the :class:`UserPermission` created
        after the request has been accepted.
        """
        up_cls = get_class('access_control', 'userpermission')
        return up_cls.objects.get_permission(self.index.object, self.user)
    
    def download_status(self):
        """Return the download status relative to the :class:`AccessRequest` instance."""
        return AccessRequest.objects.download_status_from_request(self)
    
    def __unicode__(self):
        return "%s access on (%s,%s) %s" % (self.user, self.content_type, self.object_id, self.state)
    
    class Meta:
        unique_together = (('user', 'index'),)
