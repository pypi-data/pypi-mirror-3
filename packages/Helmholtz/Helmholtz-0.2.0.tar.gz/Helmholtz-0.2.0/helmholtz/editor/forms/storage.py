#encoding:utf-8
from django import forms
from helmholtz.access_control.models import UserPermission, GroupPermission 
from helmholtz.storage.models import MimeType, FileServer, FileLocation, File, CommunicationProtocol

class CommunicationProtocolForm(forms.ModelForm):
    class Meta :
        model = CommunicationProtocol

class MimeTypeForm(forms.ModelForm):
    class Meta :
        model = MimeType

class FileServerForm(forms.ModelForm):
    class Meta :
        model = FileServer

class FileLocationForm(forms.ModelForm):
    class Meta :
        model = FileLocation
        exclude = ['server']

class FileFromLocationForm(forms.ModelForm):
    class Meta :
        model = File
        exclude = ['location']

class FileForm(forms.ModelForm):
    
    #file = forms.FileField(required=True)
    
    class Meta :
        model = File
        #exclude = ['name','filesystem','mimetype']

#class UserPermissionFromFileForm(forms.ModelForm):
#    
#    class Meta :
#        model = IntegerUserPermission
#
#class GroupPermissionFromFileForm(forms.ModelForm):
#    
#    class Meta :
#        model = IntegerGroupPermission
