from django.forms.util import ErrorList
from django import forms
from django.contrib.auth.models import User
from helmholtz.access_request.models import AccessRequest

class AccessRequestForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, widget=forms.HiddenInput())
    
    class Meta :
        model = AccessRequest
        exclude = ['auth_date', 'response_by', 'state', 'response_date']
