#encoding:utf-8
from django import forms
from django.forms.util import ErrorList
from django.db.models import Q
from django.contrib.auth.models import User, Group
from helmholtz.people.models import ScientificStructure, Researcher, PositionType, Position, EMail, Phone, Fax, WebSite, Address
#from helmholtz.acquisition.models.query import SavedQuery,DateFilter,StructureFilter,ProtocolFilter,AnimalFilter

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, help_text='100 characters max.', widget=forms.widgets.TextInput({'size':200}))
    message = forms.CharField(max_length=10000, widget=forms.widgets.Textarea({'rows':5, 'cols':80}))
    sender = forms.EmailField(help_text="Your e-mail address", widget=forms.widgets.TextInput({'size':40}))

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(u'<tr><th>%(label)s</th><td>%(errors)s%(field)s<span class="note">%(help_text)s</span></td></tr>',
                                 u'<tr><td colspan="2">%s</td></tr>',
                                 '</td></tr>',
                                 u' %s',
                                 False)

class ChangeAccessControlForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, help_text="select groups allowed to see this contact from your profile")
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False, help_text="select users allowed to see this contact from your profile")

class EMailForm(forms.ModelForm):
    
    class Meta:
        model = EMail

class PhoneForm(forms.ModelForm):
    
    class Meta:
        model = Phone

class FaxForm(forms.ModelForm):
    
    class Meta:
        model = Fax

class WebSiteForm(forms.ModelForm):
    
    class Meta:
        model = WebSite

class AddressForm(forms.ModelForm):
    
    class Meta:
        model = Address

class CreatePositionForm(forms.ModelForm):
    #researcher = forms.ModelChoiceField(queryset=Researcher.objects.all(), required=False, widget=forms.HiddenInput())
    structure = forms.ModelChoiceField(queryset=ScientificStructure.objects.all(), empty_label=None)
    end = forms.DateField(required=False)
    #position_type = forms.ModelChoiceField(label="Type", queryset=PositionType.objects.all(), empty_label=None)
    #notes = forms.CharField(required=False, widget=forms.widgets.Textarea({'rows':10}))
    
#    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
#                 initial=None, error_class=ErrorList, label_suffix=':',
#                 empty_permitted=False, instance=None, user=None, is_data_provider=False):
#        super(CreatePositionForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance)
#        #q1 = Q(scientificstructure__isnull=True)
#        #q2 = Q(permissions__integergrouppermission__group__name="admin") 
#        self.fields['structure'].queryset = self.fields['structure'].queryset.filter(parent__isnull=True)
    
    class Meta:
        model = Position
        fields = ['structure', 'start', 'end', 'position_type', 'notes']

class ChangePhotoForm(forms.Form) :
    photo = forms.ImageField(required=True)

class ChangeDescriptionForm(forms.Form) :
    description = forms.CharField(required=False, widget=forms.Textarea)

class ChangeEMailForm(forms.Form):
    email = forms.EmailField(required=True)
