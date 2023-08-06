#encoding:utf-8
from django import forms

class PermissionForm(forms.Form):
    """
    A form displaying only :class:`Permission` class fields.
    
    NB :
    
    It is a classic :class:`Form` in order to manage the creation
    of :class:`Permission` from the :class:`RequestManager` class
    rather than a :class:`ModelForm` class.
    """
    can_view = forms.BooleanField(initial=True)
    can_modify = forms.BooleanField(initial=False)
    can_delete = forms.BooleanField(initial=False)
    can_download = forms.BooleanField(initial=False)
    can_modify_permission = forms.BooleanField(initial=False)
