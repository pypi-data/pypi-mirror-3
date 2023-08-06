from django import forms
from django.contrib.auth.models import User, Group
from helmholtz.access_control.models import UnderAccessControlEntity, GroupPermission, UserPermission

class UserForm(forms.ModelForm):
    password_1 = forms.CharField(max_length=32, label='Password', widget=forms.PasswordInput(render_value=True))
    password_2 = forms.CharField(max_length=32, label='Password confirmation', widget=forms.PasswordInput(render_value=True))
    
    class Meta :
        model = User
        exclude = ['password', 'user_permissions', 'last_login', 'date_joined']
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if not kwargs.has_key('instance') :
            self.fields['password_1'].required = True
            self.fields['password_2'].required = True
        else :
            self.fields['password_1'].required = False
            self.fields['password_2'].required = False
    
    def clean_password_2(self):
        """
        Verify if password_1 and password_2 are equal.
        """
        password1 = self.cleaned_data.get('password_1')
        password2 = self.cleaned_data.get('password_2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        #retrieve the user instance correspoding to the form
        instance = super(UserForm, self).save(commit)
        #change password if field is not void
        password1 = self.cleaned_data["password_1"]
        if password1 :
            instance.set_password(password1)
        #commit password change
        if commit:
            instance.save()
        return instance

class UserFormWithoutGroups(UserForm):
    
    class Meta :
        model = User
        exclude = ['password', 'groups', 'user_permissions', 'last_login', 'date_joined']
        
class GroupForm(forms.ModelForm):
    
    class Meta :
        model = Group
        exclude = ['id', 'permissions']

class UnderAccessControlEntityForm(forms.ModelForm):
    class Meta :
        model = UnderAccessControlEntity

class UserPermissionForm(forms.ModelForm):
    
    class Meta :
        model = UserPermission
        exclude = ['index']
        fields = (
            'user',
            'can_view',
            'can_modify',
            'can_delete',
            'can_download',
            'can_modify_permission',
        )

class GroupPermissionForm(forms.ModelForm):
    
    class Meta :
        model = GroupPermission
        exclude = ['index']
        fields = (
            'group',
            'can_view',
            'can_modify',
            'can_delete',
            'can_download',
            'can_modify_permission',
        )

#class IntegerGroupPermissionFromGroupForm(forms.ModelForm):
#    class Meta :
#        model = IntegerGroupPermission
#        exclude = ['group']
#
#class CharGroupPermissionFromGroupForm(forms.ModelForm):
#    class Meta :
#        model = CharGroupPermission
#        exclude = ['group']
#
#class IntegerUserPermissionFromUserForm(forms.ModelForm):
#    class Meta :
#        model = IntegerUserPermission
#        exclude = ['user']
#
#class CharUserPermissionFromUserForm(forms.ModelForm):
#    class Meta :
#        model = CharUserPermission
#        exclude = ['user']
#
#class IntegerGroupPermissionForm(forms.ModelForm):
#    class Meta :
#        model = IntegerGroupPermission
#        exclude = ['content_type', 'object_id', 'group']
#
#class IntegerUserPermissionForm(forms.ModelForm):
#    class Meta :
#        model = IntegerUserPermission
#        exclude = ['content_type', 'object_id', 'user']
#
#class CharGroupPermissionForm(forms.ModelForm):
#    class Meta :
#        model = CharGroupPermission
#        exclude = ['content_type', 'object_id', 'group']
#
#class CharUserPermissionForm(forms.ModelForm):
#    class Meta :
#        model = CharUserPermission
#        exclude = ['content_type', 'object_id', 'user']
#
#class IntegerGroupPermissionFromFileForm(forms.ModelForm):
#    
#    class Meta :
#        model = IntegerGroupPermission
#        exclude = ['content_type', 'object_id']
#
#class IntegerUserPermissionFromFileForm(forms.ModelForm):
#    
#    class Meta :
#        model = IntegerUserPermission
#        exclude = ['content_type', 'object_id']
