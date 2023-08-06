#encoding:utf-8
from django.contrib import admin
from helmholtz.annotation.models import Descriptor, Tag, Annotation, Attachment

annotation_admin = admin.site

annotation_admin.register(Descriptor)
annotation_admin.register(Tag)
annotation_admin.register(Annotation)
annotation_admin.register(Attachment)
