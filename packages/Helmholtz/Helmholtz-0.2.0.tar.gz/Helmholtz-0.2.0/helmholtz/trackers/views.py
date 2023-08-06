#encoding:utf-8
from helmholtz.trackers.models import ConnectionTracker, Message
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def detect_connection(request, view_label):
    """Count connection each time a user connects to the website."""
    ConnectionTracker.objects.create(user=request.user)
    return HttpResponseRedirect(reverse(view_label))

def delete_message(request, message_id):
    """Delete a message."""
    message = Message.objects.get(pk=int(message_id))
    message.delete()
    return HttpResponseRedirect(request.session['last_page'])
