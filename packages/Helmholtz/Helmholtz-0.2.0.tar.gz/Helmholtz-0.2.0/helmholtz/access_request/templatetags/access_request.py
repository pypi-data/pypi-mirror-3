#encoding:utf-8
from helmholtz.access_control.models import Permission
from helmholtz.access_request.models import AccessRequest
from django import template

"""
These template tags provide the ability to include
in templates the status of a requested object and
eventually know in which format it is available. 
"""

register = template.Library()

@register.inclusion_tag('download_status.html', takes_context=True)
def download_status(context, obj, user):
    """
    Return the object and its status useful 
    to render the download status in a web page.
    
    For future release :
    
    It would be a good idea to not limit data export
    to :class:`helmholtz.storage.models.File` objects
    and extend to other models provided they have got
    a way to convert an instance to JSON or XML formats.
    """
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['status'] = AccessRequest.objects.download_status(obj, user)
    _context['file'] = obj
    return _context

@register.inclusion_tag('download_status.html', takes_context=True)
def download_status_from_request(context, request):
    """
    Return the object and its status useful 
    to render the download status in a web page.
    """
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['status'] = AccessRequest.objects.download_status_from_request(request.user)
    _context['file'] = request.object
    return _context
