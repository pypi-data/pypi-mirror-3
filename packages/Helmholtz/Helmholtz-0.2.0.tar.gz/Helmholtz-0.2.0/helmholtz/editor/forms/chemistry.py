#encoding:utf-8
from django import forms
from helmholtz.chemistry.models import Substance, Product, Solution, QuantityOfSubstance, ApplicationType

class SubstanceForm(forms.ModelForm):
    class Meta :
        model = Substance

class ProductForm(forms.ModelForm):
    class Meta :
        model = Product

class ApplicationTypeForm(forms.ModelForm):
    class Meta :
        model = ApplicationType

class SolutionForm(forms.ModelForm):
    class Meta :
        model = Solution

class QuantityOfSubstanceForm(forms.ModelForm):
    #solution = forms.ModelChoiceField(required=False, queryset=Solution.objects.all(), widget=forms.HiddenInput())
    
    class Meta :
        model = QuantityOfSubstance
        exclude = ['solution']
        
