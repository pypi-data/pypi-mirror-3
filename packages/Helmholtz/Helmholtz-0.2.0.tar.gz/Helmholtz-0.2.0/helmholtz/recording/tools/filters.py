#encoding:utf-8
from django.utils.datastructures import SortedDict
from helmholtz.core.shortcuts import get_class, get_subclasses
from helmholtz.core.schema import cast_queryset, get_subclasses_recursively, create_subclass_lookup

def get_available_object_types(model, lookup=None, value=None, leaf_class=True, proxies=False):
    if not lookup :
        instances = model.objects.all()
    else :
        assert value, "value must be specified when lookup is used"
        dct = {lookup:value}
        instances = model.objects.filter(**dct)
    subclasses = [k for k in get_subclasses_recursively(model, strict=leaf_class, proxies=proxies) if (not get_subclasses(k, proxies)) and k.objects.count()]
    counts = SortedDict()
    for subclass in subclasses :
        objects = cast_queryset(instances, subclass.__name__)
        count = objects.count()
        counts[subclass._meta.verbose_name] = count
    return counts

def get_distinct_object_types(queryset, model, prefix, leaf_class=True, proxies=False):
    types = SortedDict()
    total = 0
    counts = SortedDict()
    subclasses = [k for k in get_subclasses_recursively(model, strict=leaf_class, proxies=proxies) if (leaf_class and not get_subclasses(k, proxies) and k.objects.count()) or (not leaf_class and k.objects.count())]
    for subclass in subclasses :
        subclass_lookup = create_subclass_lookup(subclass)
        if subclass != model :
            lookup = "%s__%s__in" % (prefix, subclass_lookup)
        else :
            lookup = "%s__in" % prefix
        dct = {lookup:subclass.objects.all()}
        count = queryset.filter(**dct).distinct().count()
        if count :
            counts[subclass._meta.verbose_name] = count
            total += count
    types['quantity'] = total
    types['names'] = counts
    return types

def get_distinct_object_keys(queryset, model, prefix, attribute):
    types = SortedDict()
    total = 0
    counts = SortedDict()
    objects = model.objects.all()
    for obj in objects :
        lookup = "%s__pk" % prefix
        dct = {lookup:obj.pk}
        count = queryset.filter(**dct).distinct().count()
        if count :
            key = getattr(obj, attribute)
            counts[key] = count
            total += count
    types['quantity'] = total
    types['names'] = counts
    return types
    
def get_available_methods(queryset, prefix, leaf_class=True):
    model = get_class('equipment', 'DeviceConfiguration')
    return get_distinct_object_types(queryset, model, prefix, leaf_class)

def get_available_protocols(queryset, prefix='', leaf_class=True):
    model = get_class('stimulation', 'Stimulus')
    protocols = get_distinct_object_types(queryset, model, prefix, leaf_class)
#    #add spontaneous activity
#    dct = {prefix+'__isnull':True}
#    count = queryset.filter(**dct).distinct().count()
#    if count :
#        protocols['names']['spontaneous activity'] = count
#        protocols['quantity'] += count
    return protocols

def get_available_preparations(queryset, prefix, leaf_class=True):
    model = get_class('preparations', 'Preparation')
    return get_distinct_object_types(queryset, model, prefix, leaf_class)

