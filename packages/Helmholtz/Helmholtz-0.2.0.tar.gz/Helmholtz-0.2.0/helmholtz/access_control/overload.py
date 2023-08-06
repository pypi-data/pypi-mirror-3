#encoding:utf-8
from helmholtz.core.dependencies import get_dependencies, get_all_dependencies
from helmholtz.access_control.models import UnderAccessControlEntity, User, Permission

"""
This module provides functionalities to avoid cascading
deletion of objects that are not owned by a user.
"""

"""
Only the 'secure_delete' function could be useful to a user.
Others are just implementation detail functions.
"""

def unlink_reverse_o2o(obj, field_name, dependencies, selection):
    """Unlink object related by a one to one foreign key."""
    try :
        sub_obj = getattr(obj, field_name)
    except :
        pass
    else :
        if not (sub_obj in selection) and not dependencies[field_name]['is_required'] :    
            setattr(sub_obj, dependencies[field_name]['field'], None)
            sub_obj.save()
        make_recursion(sub_obj, selection)

def unlink_reverse_fkey(obj, field_name, dependencies, selection):
    """Unlink object related by a one to many foreign key."""
    is_required = dependencies[field_name]['is_required']
    manager = getattr(obj, field_name)
    to_dissociate = [k for k in manager.all() if not (k in selection) and not is_required] 
    
    # be careful ! remove exists only
    # for non required foreign keys
    if not is_required :
        manager.remove(*to_dissociate)
    
    # recursion is necessary only
    # when an object is selected
    to_scan = [k for k in manager.all() if k in selection]
    for sub_obj in to_scan :
        make_recursion(sub_obj, selection)

def make_recursion(sub_obj, selection):
    """A convenient function to execute delete_selection recursively."""
    new_fields = get_dependencies(sub_obj.__class__)
    if new_fields :
        delete_selection(sub_obj, selection, new_fields, False)

def delete_selection(obj, selection, fields=None, starting_point=True):
    """Realize actually the secure_delete function."""
    
    if starting_point :
        if not fields :
            fields = get_dependencies(obj.__class__)
    
    # go recursively into the object hierarchy in
    # order to remove links if objects are not in
    # selection and avoid cascaded deletion implied
    # by foreign keys
    for field in fields :
        if fields[field]['type'] == 'reverse_o2o' :
            unlink_reverse_o2o(obj, field, fields, selection)
        elif fields[field]['type'] == 'reverse_fk' :
            unlink_reverse_fkey(obj, field, fields, selection)
        elif fields[field]['type'] == 'generic_rel' :
            pass
        else :
            raise NotImplementedError('only reverse foreign keys and one to one fields are valid')       
 
    # finally remove objects stored in selection 
    # and their relative permissions
    if starting_point :
        refreshed_selection = [k.__class__.objects.get(pk=k.pk) for k in selection]
        for selected in refreshed_selection :
            if UnderAccessControlEntity.objects.is_registered(selected.__class__) :
                Permission.objects.remove_all_permissions(selected)
            selected.delete()
    
    return obj     

def get_deletable(obj, user, selection, fields, filter):
    """Return only object of the selection that are deletable by the user."""
    deletable = list()
    if selection is None :
        deletable.extend([k[1] for k in get_all_dependencies(obj, fields) if user.can_delete(k[1])])
    else :
        if selection :
            # keep objects of the selection
            # that are deletable by the user
            deletable.extend([k for k in selection if user.can_delete(k)])
            
            # filter is here to trigger an
            # exception if needed
            if not filter and (len(deletable) != len(selection)) :
                not_deletable = [k for k in selection if not k in deletable]
                raise Exception("Delete permission required on objects %s" % (not_deletable)) 
    return deletable

def delete_main_object(obj, deletable, fields):
    """
    Delegate the deletion to another object that is reflecting
    the current state of the object to delete.
    """
    delete_selection(obj, deletable, fields=fields) 
    if UnderAccessControlEntity.objects.is_registered(obj.__class__) :
        Permission.objects.remove_all_permissions(obj)
    obj.delete()
        
def secure_delete(obj, user, selection=None, filter=False):
    """
    Delete an object and all depending objects recursively
    only if the specified user has the 'can_delete' permission
    on these objects. Else objects are not deleted but link 
    to their parents will be broken.
    """
    proxy_user = User.objects.get(pk=user.pk)
    if proxy_user.can_delete(obj) :
        fields = get_dependencies(obj.__class__)
        deletable = get_deletable(obj, proxy_user, selection, fields, filter)
        delete_main_object(obj, deletable, fields)
    else :
        raise Exception("Delete permission required on %s." % (obj))
