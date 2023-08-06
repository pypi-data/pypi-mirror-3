#encoding:utf-8
from django import forms
from django.contrib.contenttypes.models import ContentType
from helmholtz.editor.models import View, Section, Entity, Constraint, TableConstraint, Field

class ViewForm(forms.ModelForm):
    class Meta: 
        model = View
        exclude = ['position', 'parent']

class SectionForm(forms.ModelForm):
    class Meta: 
        model = Section
        exclude = ['parent']
        fields = ['title', 'position']

class EntityForm(forms.ModelForm):
    class Meta: 
        model = Entity
        exclude = ['parent']
        #fields = ['name', 'position']

class ConstraintForm(forms.ModelForm):
    excluded_subclasses = forms.ModelMultipleChoiceField(queryset=ContentType.objects.all(), required=False)
    
    class Meta:
        model = Constraint
        exclude = [
            'entity',
            'form_style',
            'limit_to_one_subclass',
            'display_permissions',
            'display_tags',
            'display_annotations',
            'display_attachments',
            'in_expansion',
            'in_header'
        ]

class TableConstraintForm(forms.ModelForm):
    excluded_subclasses = forms.ModelMultipleChoiceField(queryset=ContentType.objects.all(), required=False)
    
    class Meta:
        model = TableConstraint
        exclude = [
            'entity',
            'form_style',
            'limit_to_one_subclass',
            'display_permissions',
            'display_tags',
            'display_annotations',
            'display_attachments',
            'in_expansion',
            'in_header'
        ]

class FieldForm(forms.ModelForm) :
    verbose_name = forms.CharField(max_length=500, required=False)
    
    class Meta:
        model = Field
        exclude = ['subfields']
