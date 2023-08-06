#encoding:utf-8
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from helmholtz.core.models import ObjectIndex
from helmholtz.access_control.models import UnderAccessControlEntity, \
                                            UserPermission, \
                                            GroupPermission

access_control_admin = admin.site
access_control_admin.register(User)
access_control_admin.register(Group)
access_control_admin.register(ContentType)
access_control_admin.register(ObjectIndex)
access_control_admin.register(UnderAccessControlEntity)
access_control_admin.register(UserPermission)
access_control_admin.register(GroupPermission)

