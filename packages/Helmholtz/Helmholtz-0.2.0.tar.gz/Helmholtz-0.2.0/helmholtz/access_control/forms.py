#encoding:utf-8
from django import forms
from django.forms import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    """
    Override Django's base AuthenticationForm to manage
    errors that can happen when resetting a password.
    """  
    password = forms.CharField(label="Password", required=False, widget=forms.PasswordInput)
    
    def clean(self):
        """
        Check if login information provided by a user are correct.
        
        (i) verify if the account exists and is active
        (ii) if it is the case, verify if the user has got a valid email address
        
        NB :
        
        If the user has been identified from an external authority,
        the user exist but its email address not necessarily. Consequently,
        its password must be ask or reset by this external authority.
        """ 
        # test if the user has clicked the reset button
        # if it is not the case just return the result 
        # of the superclass clean function
        reset_request = bool(self.data.get('Reset', None))
        if not reset_request :
            return super(LoginForm, self).clean()
        
        # test if the username field in not
        # empty before launching the validation
        username = self.data.get('username', None)
        if username :
            user = User.objects.filter(username=username)
            if reset_request and not user :
                raise ValidationError("This account doesn't exist.")
            elif reset_request :
                user, = user
                if not user.is_active :
                    raise ValidationError("Your account is inactive.")
                elif not user.email :
                    raise forms.ValidationError(
                        "You don't have registered an e-mail address."
                    )
            self.user_cache = user
            self.check_for_test_cookie()
            return self.cleaned_data
        
            
