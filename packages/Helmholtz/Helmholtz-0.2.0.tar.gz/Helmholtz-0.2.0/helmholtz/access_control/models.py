#encoding:utf-8
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User as DjangoUser, Group as DjangoGroup
from django.contrib.contenttypes.models import ContentType
from helmholtz.core.models import CastManager, Cast, CastQuerySet, ObjectIndex
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.core.schema import get_pk_type

"""
Data stored into a database come from
several laboratories, teams and relative
researchers. Some data could be critical 
or not sufficiently mature for a public
release. Consequently, it is necessary to
have access control mechanisms to limit
accesses to data to a specified set of
people. This module provides a per object
access control framework giving to a user
the ability to define people who can access,
modify, delete or also download its data.
"""

"""
By default, access control are not activated
for all database models. Models whose access
control is required must be registered through
the :class:`UnderAccessControlEntity` class.
Data corresponding to Models that are not
registered are considered as public.
"""

"""
Access controls are managed directly from
Permission, GroupPermission and UserPermission
object managers. GroupPermission is relative to
group access controls. UserPermission is relative
to user access controls. Permission is relative
to both kinds of access controls.
"""

"""
The User and Group classes defined in this
module extend the base django User and Group
classes in order to provide a way to retrieve
for a instance of these classes :

(i) the kind of access control it has on an object
(ii) the set of objects relative to a kind of access control.
"""

"""
By default, user groups can access the data.
The relative permission for each group is
dynamically updated when its relationship
with a user changes. This update is done via
the built-in django m2m_changed signal launches
the update_default_access_control function.
"""

class User(DjangoUser):
    """
    A proxy model extending functionalities of the Django
    base :class:`django.contrib.auth.models.User`.
    """
    
    class Meta :
        proxy = True
    
    def get_collaborators(self):
        """
        Return all :class:`django.contrib.auth.models.User` instances
        related to the same :class:`django.contrib.auth.models.Group` instances.
        """
        pks = [k.pk for k in self.groups.all()]
        return User.objects.filter(groups__pk__in=pks).exclude(pk=self.pk)
    
    def check_permission_type(self, obj, field):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.User`
        instance can access to the specified object with the specified permission type.
        """
        if self.is_superuser or not UnderAccessControlEntity.objects.is_registered(obj.__class__) :
            return True
        else :
            user_permission = Permission.objects.get_user_permission(obj, self)
            if user_permission and getattr(user_permission, field) :
                return True
            for group in self.groups.all() :
                group_permission = Permission.objects.get_group_permission(obj, group)
                if group_permission and getattr(group_permission, field) :
                    return True
            return False
    
    def filter_by_permission_type(self, queryset, field):
        """
        Filter the specified :class:`QuerySet` by permission type.
        """
        objects = queryset.all()
        if self.is_superuser or not UnderAccessControlEntity.objects.is_registered(queryset.model) :
            return objects
        else :
            arguments = {field:True}
            u_pks = [cast_object_to_leaf_class(k.index).object_id for k in getattr(self, "userpermission_set").filter(**arguments) if (k.index.content_type.model_class() == queryset.model)]
            g_pks = list()
            for group in self.groups.all() :
                pks = [cast_object_to_leaf_class(k.index).object_id for k in getattr(group, "grouppermission_set").filter(**arguments) if (k.index.content_type.model_class() == queryset.model)]
                g_pks.extend(pks)
            if u_pks or g_pks :
                pks = list()
                if u_pks :
                    pks.extend(u_pks)
                if g_pks :
                    pks.extend(g_pks)
                if pks :
                    objects = objects.filter(pk__in=pks) if pks else objects.none()
            else :
                objects = objects.none()
            return objects
            
    def is_owner(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.User`
        is one of the owners of an object.
        """
        return self.check_permission_type(obj, 'can_modify_permission')
    
    def can_view(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.User` can access an object.
        """
        return self.check_permission_type(obj, 'can_view')
            
    def can_delete(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.User` can delete an object.
        """
        return self.check_permission_type(obj, 'can_delete')
    
    def can_download(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.User` can download an object.
        """
        return self.check_permission_type(obj, 'can_download')
    
    def can_edit(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.User` can modify an object.
        """
        return self.check_permission_type(obj, 'can_modify')
    
    def get_owned(self, queryset):
        """
        Return objects owned by the specified :class:`django.contrib.auth.models.User`.
        """
        return self.filter_by_permission_type(queryset, 'can_modify_permission')
    
    def get_accessible(self, queryset):
        """
        Return objects that can be accessed by the specified :class:`django.contrib.auth.models.User`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_view')
    
    def get_deletable(self, queryset):
        """
        Return objects that can be deleted by the specified :class:`django.contrib.auth.models.User`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_delete')
    
    def get_downloadable(self, queryset):
        """
        Return objects that can be downloaded by the specified :class:`django.contrib.auth.models.User`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_download')
    
    def get_editable(self, queryset):
        """
        Return objects that can be modified by the specified :class:`django.contrib.auth.models.User`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_modify')

class Group(DjangoGroup):
    """
    A proxy extending functionalities to the django base :class:`django.contrib.auth.models.Group`.
    """
    
    class Meta :
        proxy = True
    
    def respect_permission_type(self, obj, field):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.Group` can access to an object.
        """
        if UnderAccessControlEntity.objects.is_under_access_control(obj.__class__) :
            group_permission = GroupPermission.objects.get_permission(obj, self)
            if group_permission and getattr(group_permission, field) :
                return True
            return False  
        else :
            return True
    
    def filter_by_permission_type(self, queryset, field):
        """
        Filter the specified :class:`QuerySet` by permission type.
        """
        objects = queryset.all()
        if UnderAccessControlEntity.objects.is_registered(queryset.model) :
            arguments = {field:True}
            pks = [cast_object_to_leaf_class(k.index).object_id for k in getattr(self, "grouppermission_set").filter(**arguments) if (k.index.content_type.model_class() == queryset.model)]
            if pks :
                objects = objects.filter(pk__in=pks) if pks else objects.none()
            else :
                objects = objects.none()
        return objects
    
    def is_owner(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.Group` is one of the owners of an object.
        """
        return self.respect_permission_type(obj, 'can_modify_permission')
    
    def can_view(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.Group` can access an object.
        """
        return self.respect_permission_type(obj, 'can_view')
            
    def can_delete(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.Group` can delete an object.
        """
        return self.respect_permission_type(obj, 'can_delete')
    
    def can_download(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.Group` can download an object.
        """
        return self.respect_permission_type(obj, 'can_download')
    
    def can_edit(self, obj):
        """
        Return a boolean telling if a :class:`django.contrib.auth.models.Group` can modify an object.
        """
        return self.respect_permission_type(obj, 'can_modify')
    
    def get_owned(self, queryset):
        """
        Return objects owned by the specified :class:`django.contrib.auth.models.Group`.
        """
        return self.filter_by_permission_type(queryset, 'can_modify_permission')
    
    def get_accessible(self, queryset):
        """
        Return objects that can be accessed by the specified :class:`django.contrib.auth.models.Group`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_view')
    
    def get_deletable(self, queryset):
        """
        Return objects that can be deleted by the specified :class:`django.contrib.auth.models.Group`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_delete')
    
    def get_downloadable(self, queryset):
        """
        Return objects that can be downloaded by the specified :class:`django.contrib.auth.models.Group`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_download')
    
    def get_editable(self, queryset):
        """
        Return objects that can be modified by the specified :class:`django.contrib.auth.models.Group`.
        """ 
        return self.filter_by_permission_type(queryset, 'can_modify')

class UACManager(models.Manager):
    """
    Manage :class:`UnderAccessControl` objects.
    """
    
    def is_registered(self, cls):
        """
        Return a boolean telling if a class is under access control.
        """
        entity = ContentType.objects.get_for_model(cls)
        uac_entity = UnderAccessControlEntity.objects.filter(entity=entity)
        return bool(uac_entity.count())
    
    def register(self, cls):
        """
        Set a class under access control.
        """
        entity = ContentType.objects.get_for_model(cls)
        assert (entity.model != 'underaccesscontrolentity') and (entity.app_label != "access_control"), "class %s.%s cannot be under access control" % (cls.__module__, cls.__name__)
        under_access_control_entity, created = UnderAccessControlEntity.objects.get_or_create(entity=entity)
        return under_access_control_entity, created
    
    def unregister(self, cls):
        """
        Disable access control for the specified class.
        """
        ct = ContentType.objects.get_for_model(cls)
        UnderAccessControlEntity.objects.get(entity=ct).delete()

class UnderAccessControlEntity(models.Model):
    """
    Enable the Helmholtz access control system for a model :
    
    ``entity`` : the :class:`ContentType` object to put under access control.
    
    ``can_be_downloaded`` : a boolean telling if instances of ``entity`` could be downloaded.
    
    """
    entity = models.OneToOneField(ContentType, primary_key=True)
    can_be_downloaded = models.NullBooleanField(null=True, blank=True)
    
    objects = UACManager()
    
    class Meta :
        verbose_name_plural = "under access control entities"
    
    def __unicode__(self):
        st = self.entity.model_class().__name__
        if self.can_be_downloaded :
            st += ' (D)' # to make the distinction between downloadable classes and others
        return st
    
    def delete(self):
        """
        Override the default delete function to cascade removing
        of :class:`helmholtz.access_control.models.Permission` objects.
        """ 
        Permission.objects.filter(index__content_type=self.entity).delete()
        super(UnderAccessControlEntity, self).delete()

class PermissionQuerySet(CastQuerySet):
    """
    A convenient class to identify a :class:`QuerySet`
    storing only :class:`Permission` instances.
    """
    pass

class BasePermissionManager(CastManager):
    """
    Enable management of per object access controls directly from
    the :class:`helmholtz.access_control.models.Permission` class.
    """
    def get_query_set(self):
        return PermissionQuerySet(self.model, using=self._db)

    def get_all_permissions(self, obj):
        """
        Return the :class:`helmholtz.access_control.models.Permission`
        instances relative to an object and permission type.
        """
        index = ObjectIndex.objects.get_registered_object(obj)
        return index.object_permissions.all() if not index is None else Permission.objects.none()
    
    def create_default_permissions(self, obj, owner):
        """
        Create a default :class:`helmholtz.access_control.models.Permission`
        instance for an object. Total access is only allowed to the owner.
        """
        assert UnderAccessControlEntity.objects.is_registered(obj.__class__), "access control not defined for class %s" % (obj.__class__)
        content_type = ContentType.objects.get_for_model(obj.__class__)
        uac_entity = UnderAccessControlEntity.objects.get(entity=content_type)
        can_download = uac_entity.can_be_downloaded
        parameters = {
            'can_view':True,
            'can_modify':True,
            'can_delete':True,
            'can_modify_permission':True,
            'can_download':can_download
        }
        UserPermission.objects.create_permission(obj, owner, **parameters)
        # add basic access to user groups 
        parameters = {
            'can_view':True,
            'can_modify':False,
            'can_delete':False,
            'can_modify_permission':False,
            'can_download':False
        }
        for group in owner.groups.all() :
            GroupPermission.objects.create_permission(obj, group, **parameters)
    
    def update_permission_parameters(self, permission, **kwargs):
        """Update :class:`helmholtz.access_control.models.Permission` parameters."""
        for arg in kwargs :
            setattr(permission, arg, kwargs[arg])
        permission.save()
        return permission
    
    def remove_all_permissions(self, obj):
        """
        Remove all kinds of :class:`helmholtz.access_control.models.Permission`
        instances corresponding to a specified object.
        """
        UserPermission.objects.remove_permissions(obj)
        GroupPermission.objects.remove_permissions(obj)

class PermissionManager(BasePermissionManager):
    """
    Enable management of per object access controls directly from
    the :class:`helmholtz.access_control.models.Permission` class.
    """
    
    def create_user_permission(self, obj, user, **kwargs):
        """
        Create a new :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        return UserPermission.objects.create_permission(obj, user, **kwargs)
    
    def get_user_permissions(self, obj):
        """
        Return the :class:`helmholtz.access_control.models.UserPermission`
        instances for the specified object.
        """
        return UserPermission.objects.get_permissions(obj)
    
    def get_user_permission(self, obj, user):
        """
        Return the :class:`helmholtz.access_control.models.UserPermission` instances
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        return UserPermission.objects.get_permission(obj, user)
    
    def remove_user_permission(self, obj, user):
        """
        Remove the :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        return UserPermission.objects.remove_permission(obj, user)
    
    def remove_user_permissions(self, obj):
        """
        Remove the :class:`helmholtz.access_control.models.UserPermission` instances
        for the specified object.
        """
        return UserPermission.objects.remove_permissions(obj)
    
    def set_user_permission(self, obj, user, **kwargs):
        """
        Update the :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        return UserPermission.objects.set_permission(obj, user, **kwargs)
    
    def create_group_permission(self, obj, group, **kwargs):
        """
        Create the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        return GroupPermission.objects.create_permission(obj, group, **kwargs)
    
    def get_group_permissions(self, obj):
        """
        Return the :class:`helmholtz.access_control.models.GroupPermission`
        instances for the specified object.
        """
        return GroupPermission.objects.get_permissions(obj)
    
    def get_group_permission(self, obj, group):
        """
        Create the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        return GroupPermission.objects.get_permission(obj, group)
    
    def remove_group_permission(self, obj, group):
        """
        Remove the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        GroupPermission.objects.remove_permission(obj, group)
    
    def remove_group_permissions(self, obj):
        """
        Remove the :class:`helmholtz.access_control.models.GroupPermission` instances
        for the specified object.
        """
        GroupPermission.objects.remove_permissions(obj)
        
    def set_group_permission(self, obj, group, **kwargs):
        """
        Update the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        GroupPermission.objects.set_permission(obj, group, **kwargs)

class Permission(Cast):
    """
    Define a :class:`helmholtz.access_control.models.UserPermission`
    or :class:`helmholtz.access_control.models.GroupPermission` types
    on an object :
    
    ``index`` : the :class:`ObjectIndex` instance linked to the permission.
    
    ``can_view`` : a boolean telling if an object could be viewed by a user / group in a template.
    
    ``can_modify`` : a boolean telling if user / group can modify an object.
    
    ``can_delete`` : a boolean telling if user / group can delete an object.
    
    ``can_download`` : a boolean telling if user / group can delete an object.
    
    ``can_modify_permission`` : a boolean telling if a permission on an object can be modified by a user / group.
    
    ``objects``: the manager handling permissions.
    """
    index = models.ForeignKey(ObjectIndex, related_name="object_permissions")
    can_view = models.BooleanField(verbose_name='view', default=True, null=False)
    can_modify = models.BooleanField(verbose_name='modify', default=False, null=False)
    can_delete = models.BooleanField(verbose_name='delete', default=False, null=False)
    can_download = models.BooleanField(verbose_name='download', default=False, null=False)
    can_modify_permission = models.BooleanField(verbose_name='is owner', default=False, null=False)
    objects = PermissionManager()
    
    class Meta:
        ordering = ['id']
    
    @property
    def object(self):
        """
        Return the object on which is applied a :class:`helmholtz.access_control.models.Permission`. 
        """
        return self.index.cast().object
    
    def __unicode__(self):
        """
        Return a string resuming all :class:`helmholtz.access_control.models.Permission` types for an object.
        """
        # cast the object in order to have a consistent
        # unicode string through subclasses
        ct_object = self.object
        cast = self.cast()
        st = "permission (%s) on %s(%s, %s)" % (self.code, ct_object.__class__.__name__, ct_object.pk, self.object)
        if hasattr(self, 'group') :
            user_or_group = cast.group
        elif hasattr(self, 'user') :
            user_or_group = cast.user
        else :
            user_or_group = None
        if user_or_group :
            st = "%s %s has %s" % (user_or_group.__class__.__name__, user_or_group, st)
        return st
    
    @property
    def code(self):
        """Return a string resuming all :class:`helmholtz.access_control.models.Permission`
        types defined in the following order :
        
            ``can_view`` : v
            ``can_modify`` : m
            ``can_delete`` : d
            ``can_download`` : D
            ``can_modify_permission`` : M
        """
        code = ''
        if self.can_view :
            code += 'v'
        if self.can_modify :
            code += 'm'
        if self.can_delete :
            code += 'd'
        if self.can_download :
            code += 'D'
        if self.can_modify_permission :
            code += 'M'
        return code

class UPManager(BasePermissionManager) :
    """
    Enable management of per object access controls from
    the :class:`helmholtz.access_control.models.UserPermission` class.
    """
    
    def create_permission(self, obj, user, **kwargs):
        """
        Create the :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        index = ObjectIndex.objects.register_object(obj)
        return UserPermission.objects.create(user=user, index=index, **kwargs)
    
    def get_permissions(self, obj):
        """
        Return the :class:`helmholtz.access_control.models.UserPermission` instances
        for the specified object.
        """
        permissions = self.get_all_permissions(obj)
        return permissions.cast(UserPermission)
    
    def get_permission(self, obj, user):
        """
        Return the :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        cls = obj.__class__
        pk_type = get_pk_type(cls)
        permissions = user.userpermission_set.filter(index__content_type__app_label=cls._meta.app_label,
                                                     index__content_type__model=cls.__name__.lower() 
        )
        
        if pk_type == int :
            permissions = permissions.filter(index__integerobjectindex__object_id=obj.pk)
        else :
            permissions = permissions.filter(index__charobjectindex__object_id=obj.pk)
        return permissions.get() if permissions else None
    
    def remove_permission(self, obj, user):
        """
        Remove the :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        permission = UserPermission.objects.get_permission(obj, user) 
        if permission :
            permission.delete()
    
    def remove_permissions(self, obj):
        """
        Remove the :class:`helmholtz.access_control.models.UserPermission` instances
        for the specified object.
        """
        user_permissions = self.get_permissions(obj)
        user_permissions.delete()
    
    def set_permission(self, obj, user, **kwargs):
        """
        Update the :class:`helmholtz.access_control.models.UserPermission` instance
        for the specified :class:`django.contrib.auth.models.User` and object.
        """
        permission = self.get_permission(obj, user)
        if permission :
            self.update_permission_parameters(permission, **kwargs)    
        else :
            self.create_permission(obj, user, **kwargs) 

class GPManager(BasePermissionManager):
    """
    Enable management of per object access controls from
    the :class:`helmholtz.access_control.models.GroupPermission` class.
    """
    
    def create_permission(self, obj, group, **kwargs):
        """
        Create the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        index = ObjectIndex.objects.register_object(obj)
        return GroupPermission.objects.create(group=group, index=index, **kwargs)
    
    def get_permissions(self, obj):
        """
        Return the :class:`helmholtz.access_control.models.GroupPermission` instances
        for the specified object.
        """
        permissions = self.get_all_permissions(obj)
        return permissions.cast(GroupPermission)
    
    def get_permission(self, obj, group):
        """
        Return the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        cls = obj.__class__
        pk_type = get_pk_type(cls)
        permissions = group.grouppermission_set.filter(
            index__content_type__app_label=cls._meta.app_label,
            index__content_type__model=cls.__name__.lower() 
        )
        if pk_type == int :
            permissions = permissions.filter(index__integerobjectindex__object_id=obj.pk)
        else :
            permissions = permissions.filter(index__charobjectindex__object_id=obj.pk)
        return permissions.get() if permissions else None
    
    def remove_permission(self, obj, group):
        """
        Remove the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        permission = GroupPermission.objects.get_permission(obj, group) 
        if permission :
            permission.delete()
    
    def remove_permissions(self, obj):
        """
        Remove the :class:`helmholtz.access_control.models.GroupPermission` instances
        for the specified object.
        """
        group_permissions = self.get_permissions(obj)
        group_permissions.delete()
    
    def set_permission(self, obj, group, **kwargs):
        """
        Update the :class:`helmholtz.access_control.models.GroupPermission` instance
        for the specified :class:`django.contrib.auth.models.Group` and object.
        """
        permission = self.get_permission(obj, group)
        if permission :
            self.update_permission_parameters(permission, **kwargs)    
        else :
            self.create_permission(obj, group, **kwargs) 

class UserPermission(Permission):
    """
    Define :class:`helmholtz.access_control.models.UserPermission`
    on an object for a :class:`django.contrib.auth.models.User` instance.
    """
    user = models.ForeignKey(DjangoUser)
    
    objects = UPManager()
    
    def clean(self):
        """
        Check if a :class:`helmholtz.access_control.models.UserPermission`
        is already registered for a (`django.contrib.auth.models.User`, object)
        tuple. Raise a :class:`ValidationError` if its the case.
        """
        try :
            self.__class__.objects.get(index=self.index, user=self.user)
            raise ValidationError('%s cannot have permission on %s twice' % (self.user, self.index))
        except :
            pass
    
    class Meta :
        ordering = ['id']
        
class GroupPermission(Permission):
    """
    Define :class:`helmholtz.access_control.models.GroupPermission`
    on an object for a :class:`django.contrib.auth.models.Group` instance.
    """
    group = models.ForeignKey(DjangoGroup)
    
    objects = GPManager()
    
    def clean(self):
        """
        Check if a :class:`helmholtz.access_control.models.GroupPermission`
        is already registered for a (`django.contrib.auth.models.Group`, object)
        tuple. Raise a :class:`ValidationError` if its the case.
        """
        try :
            self.__class__.objects.get(
                index=self.index,
                user=self.user
            )
            raise ValidationError('%s cannot have permission on %s twice : %s' % (self.group, self.index, self))
        except :
            pass
    
    class Meta :
        ordering = ['id']

def is_base_permission(permission):
    """
    Return a boolean telling if a :class:`helmholtz.access_control.models.Permission`
    corresponding to a default access_control, i.e only ``can_view`` attribute is set to True.
    """
    return permission.can_view and not (permission.can_modify or permission.can_delete or permission.can_modify_permission or permission.can_download)

def create_or_remove_group_permissions(users, groups, action):
    """
    Update the list of default access control on an object.
    
    First, get objects owned by each users. Then, for each object try to
    get a :class:`helmholtz.access_control.models.GroupPermission` for each
    `django.contrib.auth.models.Group` :
    
    (i) if the permission doesn't exist for a ``post_add`` signal create a default one
    (ii) else remove the permission if it doesn't correspond to a default one instance for
    a ``post_remove`` or ``post_clear`` signal.
    """
    
    parameters = {
        'can_view':True,
        'can_modify':False,
        'can_delete':False,
        'can_modify_permission':False,
        'can_download':False
    }
    for user in users :
        objects = objects = [k.object for k in user.userpermission_set.filter(can_modify_permission=True)]
        for obj in objects :
            for group in groups :
                permission = GroupPermission.objects.group_permission(obj, group)
                if not permission and (action == 'post_add') :
                    GroupPermission.objects.create_permission(obj, group, **parameters)
                elif permission and is_base_permission(permission) and (action in ['post_remove', 'post_clear']) :
                    permission.delete()

def update_default_access_control(sender, **kwargs):
    """
    Update dynamically default access control to an object
    when relationships between users and groups change.
    """
    # update is triggered when action is a post_add, post_remove or post_clear signal
    # and the relationships between users and groups are changed
    if not (kwargs['action'].startswith('post') and issubclass(kwargs['model'], (DjangoUser, DjangoGroup))) :
        return
    
    model, pk_set, action = kwargs['model'], kwargs['pk_set'], kwargs['action']
    # get the users and groups whose relationships is modified
    if issubclass(model, DjangoUser) :
        # forward changes
        user = kwargs['instance']
        groups = DjangoGroup.objects.filter(pk__in=pk_set) \
            if action in ['post_add', 'post_remove'] \
            else user.groups.all()
        users = [user]
    elif issubclass(model, DjangoGroup) :
        # backward changes
        group = kwargs['instance']
        users = DjangoUser.objects.filter(pk__in=pk_set) \
            if action in ['post_add', 'post_remove'] \
            else group.user_set.all()
        groups = [group]
    # finally create or remove the permission
    # depending on the type of action
    create_or_remove_group_permissions(users, groups, action)

# automatize access control when the relationships
# between users and groups are changed
#signals.m2m_changed.connect(update_default_access_control)

# register objects that are under access control
def register_for_access_control(sender, **kwargs):
    """Unregister a :class:`ObjectIndex` right after its relative object deletion."""
    if UnderAccessControlEntity.objects.is_registered(kwargs['instance'].__class__) :
        ObjectIndex.objects.register_object(kwargs['instance'])

signals.post_save.connect(register_for_access_control)
