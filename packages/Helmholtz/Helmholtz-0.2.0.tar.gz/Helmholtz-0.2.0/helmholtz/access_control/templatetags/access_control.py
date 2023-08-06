#encoding:utf-8
from helmholtz.access_control.models import Permission
from django import template

"""
These template tags provide the ability to include in templates the
the kind of permissions that are applied on objects for a set of users. 
"""

register = template.Library()

@register.inclusion_tag('access_control.html')
def permissions(context, obj):
    """
    Return :class:`helmholtz.access_control.models.GroupPermission`
    and :class:`helmholtz.access_control.models.UserPermission` instances
    relative to the a specified object in order to render who can
    or cannot access to an object and their relative access control types.
    """
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['gpermissions'] = Permission.objects.get_group_permissions(obj)
    _context['upermissions'] = Permission.objects.get_user_permissions(obj)
    return _context
