#encoding:utf-8
from django import forms
from helmholtz.people.models import SkillType, Supplier, Address, EMail, Phone, Fax, WebSite, Contact, ScientificStructure, Researcher, Position, PositionType

class AddressForm(forms.ModelForm):
    class Meta :
        model = Address

class EMailForm(forms.ModelForm):
    class Meta :
        model = EMail
        
class PhoneForm(forms.ModelForm):
    class Meta :
        model = Phone

class FaxForm(forms.ModelForm):
    class Meta :
        model = Fax

class WebSiteForm(forms.ModelForm):
    class Meta :
        model = WebSite

class ContactForm(forms.ModelForm):
    class Meta :
        model = Contact

class SkillTypeForm(forms.ModelForm):
    class Meta :
        model = SkillType

class ScientificStructureForm(forms.ModelForm):
    class Meta :
        model = ScientificStructure
        exclude = ['parent', 'contacts']

class ScientificStructureWithoutGroupForm(forms.ModelForm):
    class Meta :
        model = ScientificStructure
        exclude = ['contacts', 'db_group']

class SupplierForm(forms.ModelForm):
    class Meta :
        model = Supplier
        exclude = ['contacts']

class PositionTypeForm(forms.ModelForm):
    class Meta :
        model = PositionType

class PeoplePositionForm(forms.ModelForm):
    class Meta :
        model = Position
        exclude = ['researcher']

class PositionFromStructureForm(forms.ModelForm):
    class Meta :
        model = Position
        exclude = ['structure']

class PositionFromResearcherForm(forms.ModelForm):
    class Meta :
        model = Position
        exclude = ['researcher']

class ResearcherForm(forms.ModelForm):
    class Meta :
        model = Researcher
        exclude = ['contacts']

class ResearcherWithoutUserForm(forms.ModelForm):
    class Meta :
        model = Researcher
        exclude = ['contacts', 'user']
