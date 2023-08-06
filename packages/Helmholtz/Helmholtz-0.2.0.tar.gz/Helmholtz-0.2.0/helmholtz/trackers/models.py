#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User, Group
from helmholtz.core.models import Cast

class ConnectionTracker(models.Model):
    """Stores each time a :class:`django.contrib.auth.models.User` connects to the website."""
    user = models.ForeignKey(User, related_name="connections")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta :
        verbose_name = "connection"
    
    def __unicode__(self):
        return "%s : %s" % (self.date, self.user.username) 

class Message(Cast):
    """Stores messages sent by a :class:`django.contrib.auth.models.User`."""
    sender = models.ForeignKey(User, related_name="mails_as_sender")
    date = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    email = models.EmailField(null=True, blank=True)
    recipients = models.ManyToManyField(User, related_name="mails_as_recipient")
        
    def __unicode__(self):
        return "%s, %s : %s" % (self.sender.username, self.date, self.subject) 
    
    class Meta:
        ordering = ['-date']
