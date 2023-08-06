#encoding:utf-8
from django import forms
from helmholtz.annotation.models import Tag, Annotation, Attachment, StaticDescription

class TagForm(forms.ModelForm):
    class Meta :
        model = Tag
        exclude = ['content_type_objects']

class AnnotationForm(forms.ModelForm):
    class Meta :
        model = Annotation
        exclude = ['content_type_objects']

class AttachmentForm(forms.ModelForm):
    class Meta :
        model = Attachment
        exclude = ['content_type_objects']

class StaticDescriptionForm(forms.ModelForm):
    class Meta :
        model = StaticDescription
