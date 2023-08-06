#encoding:utf-8
from datetime import datetime
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.db.models import Q, ManyToManyField, ForeignKey
from django.db.models.related import RelatedObject
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor, ManyRelatedObjectsDescriptor, ReverseManyRelatedObjectsDescriptor
from django.forms import HiddenInput
from django.forms.models import ModelForm
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.forms import ChoiceField, ModelChoiceField, ModelMultipleChoiceField
from django.contrib.contenttypes.models import ContentType 
from helmholtz.editor.models import Constraint
from django.forms import Form, ModelMultipleChoiceField, ModelChoiceField, DateTimeField, BooleanField, CharField, IntegerField, FloatField
from helmholtz.core.models import Cast, HierarchicalStructure, ObjectIndex
from helmholtz.core.schema import get_all_fields, get_parents_recursively, get_subclasses_recursively, get_parent_chain, get_all_children
from helmholtz.core.dependencies import get_all_dependencies, get_dependencies, get_all_links
from helmholtz.access_control.models import UnderAccessControlEntity, User, Permission
from helmholtz.access_control.overload import secure_delete
from helmholtz.annotation.models import Tag
from helmholtz.measurements.models import Parameter, GenericMeasurement, BoolMeasurement, IntegerMeasurement, FloatMeasurement, StringMeasurement
from helmholtz.recording.models import RecordingConfiguration
from helmholtz.units.models import Unit, BaseUnit
from helmholtz.units.fields import UnitWidget
from helmholtz.editor.models import Entity
from helmholtz.editor.forms.measurements import MeasurementField, MeasurementWidget 

def one_help_text_at_least(form):
    """Detect if a form must be display a help text row."""
    for field in form :
        if field.help_text :
            return True
    return False

def is_fake_object_link(node_type, cls, field):
    related = (ForeignRelatedObjectsDescriptor, ManyRelatedObjectsDescriptor, ReverseManyRelatedObjectsDescriptor)
    return (node_type == 'objectlink') and isinstance(getattr(cls, field), related)

def request_context(view_func):
    """Decorator to wrap the context dictionary into a RequestContext."""
    def modified_function(self, *args, **kwargs):
        context = view_func(self, *args, **kwargs)
        return RequestContext(self.request, context)
    modified_function.__doc__ = view_func.__doc__
    return modified_function

def render_to(template_name):
    """Decorator that do template rendering from a context."""
    def renderer(func):
        def wrapper(self, *args):
            output = func(self, *args)
            if isinstance(output, RequestContext) :
                context = output
            elif isinstance(output, dict) : 
                context = RequestContext(self.request, output)
            else :
                raise NotImplementedError("this decorator works with context defined as a dictionary or a RequestContext")
            return render_to_response(template_name, context)
        return wrapper
    return renderer

class EditionFormFactory(object):
    """Generate Form corresponding to a specific Model."""
    
    def __init__(self, cls):
        self.cls = cls
    
    def _get_model_form(self, excluded=[]) :
        """Return the default form correspoding to the model."""
        class DefaultForm(ModelForm):
            class Meta :
                model = self.cls
                if excluded :
                    exclude = excluded
        return type("%sDefaultForm" % self.cls.__name__, (DefaultForm,), {})
        
    def _reset_choices(self, form_type, user):
        """
        Change dynamically model choice fields in order 
        to display only data accessible to the request user.
        """
        proxy_user = User.objects.get(pk=user.pk)
        for field in form_type.base_fields :
            field_obj = form_type.base_fields[field]
            if (isinstance(field_obj, ModelMultipleChoiceField) or isinstance(field_obj, ModelChoiceField)) and UnderAccessControlEntity.objects.is_registered(field_obj.queryset.model):
                field_obj.queryset = proxy_user.get_accessible(field_obj.queryset)
    
    def _cast_links(self, form):
        """Cast fields corresponding to objects to their actual types."""
        for field in form.cleaned_data :
            obj = form.cleaned_data[field]
            if isinstance(obj, Cast) :
                form.cleaned_data[field] = obj.cast()
    
    def _detect_excluded_in_unique_together(self, form_type):
        """Return fields that are mentioned both in model unique_together and form exclude."""
        fields = list()
        exclude = form_type._meta.exclude
        if exclude :
            unique = self.cls._meta.unique_together
            for field in exclude :
                for item in unique :
                    if field in item and not field in fields :
                        fields.append(field)
        return fields
    
    def _complete_with_hidden_field(self, form_type, field_name, parent_object):
        """
        Create and initialize the value of an hidden field corresponding to a field 
        defined in unique_together and corresponding to the parent object to which 
        an object will be linked.
        
        NB : Necessary because the link to the parent object is done after 
        instance = form.save() that raises an IntegrityError implied by the fact 
        that related field comes with a NULL value that is incompatible
        with the unique_together constraint.
        """ 
        excluded = [k for k in form_type._meta.exclude if k != field_name]
        form = self._get_model_form(excluded=excluded)
        dct = dict()
        dct[field_name] = deepcopy(form.base_fields[field_name])
        dct[field_name].widget = HiddenInput()
        dct[field_name].initial = parent_object.pk
        form_type = type(form_type.__name__ + "WithAutoHiddenField", (form_type,), dct)
        form_type._meta.exclude = excluded
        return form_type
    
    def _init_hidden_field(self, form_type, field_name, parent_object):
        """
        Initialize the value of an hidden field defined in unique_together 
        and corresponding to the parent object to which an object will be linked.
        
        NB 1 : This initialization is necessary because the link to the parent object 
        is done after instance = form.save() that raises an IntegrityError implied 
        by the fact that the hidden field comes with a NULL value that is incompatible
        with the unique_together constraint.
        
        NB 2 : In future release this function will be replaced by _complete_with_hidden_field
        that creates automatically the hidden field and then initialize it.
        """ 
        form_type.base_fields[field_name].initial = parent_object.pk
        return form_type
    
    def _get_field_corresponding_to_parent_object(self, parent_object, field_name=None):
        """Return the field name corresponding to the key to the parent object."""
        field = parent_object._meta.get_field_by_name(self.cls.__name__.lower())[0]
        return field.field.name
    
    def _get_user_defined_forms(self, form, parent_object=None, field_name=None):
        """Import then return the user defined form to create or update an object."""
        _sp = form.split('.')
        module = __import__('.'.join(_sp[0:-1]))
        for _md in _sp[1:-1]:
            module = getattr(module, _md) 
        form_type = getattr(module, _sp[-1])
        if parent_object :
            fields = self._detect_excluded_in_unique_together(form_type)
            if fields :
                name = self._get_field_corresponding_to_parent_object(parent_object)
            else :
                name = field_name
            #create and init an hidden field to avoid IntegrityError
            if name in fields :
                form_type = self._complete_with_hidden_field(form_type, name, parent_object)
        return form_type

    def _get_form_type(self, form=None, user=None, parent_object=None, field_name=None):
        """Get the form type from a constraint object."""
        if form :
            form_type = self._get_user_defined_forms(form, parent_object, field_name)
        else :
            form_type = self._get_model_form()
        if user :
            self._reset_choices(form_type, user)
        return form_type
    
    def _reset_textarea(self, form_obj):
        """Reset textarea cols and rows."""
        for field in form_obj.fields :
            if form_obj.fields[field].__class__.__name__ in ['ImageField', 'CharField', 'PhysicalQuantityField'] :        
                if form_obj.fields[field].widget.__class__.__name__ in ['Textarea', 'PasswordInput'] :
                    if form_obj.fields[field].widget.attrs.has_key("cols") :
                        form_obj.fields[field].widget.attrs.pop("cols")
                    if form_obj.fields[field].widget.attrs.has_key("rows") :
                        form_obj.fields[field].widget.attrs['rows'] = 1
    
    def createGetInsertionForm(self, user, prefix, form=None, parent_object=None, field_name=None):
        """Create a form for a new object."""
        form_type = self._get_form_type(form, user, parent_object, field_name)
        if form_type._meta.model.__name__ == 'AccessRequest' :
            form_obj = form_type(initial={'user':user.pk}, prefix=prefix)
        else :
            form_obj = form_type(prefix=prefix)
        return form_obj
    
    def createPostInsertionForm(self, user, post, files, prefix, form=None, parent_object=None, field_name=None):
        """Create a form to validate a new object."""
        form_type = self._get_form_type(form, user, parent_object, field_name)
        form_obj = form_type(post, files, prefix=prefix)
        return form_obj
    
    def createGetModifyForm(self, instance, user, prefix, form=None, parent_object=None, field_name=None):
        """Create a form displaying data of an existing object."""
        form_type = self._get_form_type(form, user, parent_object, field_name)
        form_obj = form_type(instance=instance, prefix=prefix)
        return form_obj
    
    def createPostModifyForm(self, instance, user, post, files, prefix, form=None, parent_object=None, field_name=None):
        """Create a form to validate modified data of an existing object."""
        form_type = self._get_form_type(form, user, parent_object, field_name)
        form_obj = form_type(post, files, instance=instance, prefix=prefix)
        return form_obj
    
    def createSingleObjectChoiceForm(self, queryset, post=None):
        """Create a form displaying a ModelChoiceField."""
        field = ModelChoiceField(queryset=queryset, required=True, empty_label=None, help_text="This field is a one to one relationship, existing link will be replaced by the new one.")
        form_type = type('SingleObjectChoiceForm', (Form,), {'List of %s' % queryset.model._meta.verbose_name_plural.lower():field})
        if queryset :
            if not post :
                return form_type(prefix='form')
            else :
                return form_type(post, prefix='form')
        else :
            return None
    
    def createSeveralObjectsChoiceForm(self, queryset, post=None):
        """Create a form displaying a ModelMultipleChoiceField."""
        field = ModelMultipleChoiceField(queryset=queryset, required=True)
        form_type = type('SeveralObjectsChoiceForm', (Form,), {'List of %s' % queryset.model._meta.verbose_name_plural.lower():field})
        if queryset :
            if not post :
                return form_type(prefix='form')
            else :
                return form_type(post, prefix='form')
        else :
            return None
    
    def createSubclassChoiceForm(self, subclasses, prefix):
        """Create a form displaying the class of the future object to create."""
        if subclasses :
            choices = list()
            for ct in subclasses :
                choices.append((ct.pk, ct.model_class()._meta.verbose_name.title()))
                field = ChoiceField(choices=choices, required=True)
            form_type = type('SubclassChoiceForm', (Form,), {"%s type" % self.cls.__name__:field})
            return form_type(prefix=prefix)
        else :
            return None
    
    def createParameterChoiceForm(self, prefix):
        """Create a form displaying a ModelChoiceField containing Parameter objects relative to the class."""
        #special case when self.cls is a subclass of RecordingConfiguration
        #and the parameter list id constrained by a DeviceConfiguration
        all_classes = list()
        all_classes.extend(get_parents_recursively(self.cls))
        all_classes.insert(0, self.cls)
        ctypes = [ContentType.objects.get_for_model(k) for k in all_classes]
        parameters = Parameter.objects.filter(content_type__in=ctypes)
        if parameters :
            field = ModelChoiceField(queryset=parameters, required=True, empty_label=None)
            form_type = type('ParameterChoiceForm', (Form,), {"parameter":field})
            return form_type(prefix=prefix)
        else :
            return None
    
    def createMeasurementForm(self, parameter, prefix, data=None, value=None, instance=None):    
        dct = SortedDict()
        dct['timestamp'] = DateTimeField(initial=datetime.now())
        initial_value = value.value if value else None
        if parameter.pattern :
            #set up a choice field corresponding to the parameter pattern
            values = parameter.get_values()
            if parameter.get_type().__name__ != 'ModelBase' :
                
                choices = [(k, str(k)) for k in values]
                dct['value'] = ChoiceField(choices=choices, initial=initial_value, required=True)    
            else :
                raise NotImplementedError()
                dct['value'] = ModelChoiceField(queryset=values, initial=values[0].pk if values.count() else None, required=True) 
        else :
            #set up the field type corresponding to the parameter type
            fields = {
                'B':BooleanField(required=True, initial=initial_value),
                'I':IntegerField(required=True, initial=initial_value),
                'F':FloatField(required=True, initial=initial_value),
                'S':CharField(max_length=32, required=True, initial=initial_value) 
            }
            try :
                dct['value'] = fields[parameter.type]
            except :
                raise NotImplementedError()
        #set up the unit choice  
        if parameter.unit :  
            initial_unit = parameter.unit.cast() if (not value or not value.unit) else value.unit.cast()
            root_unit = initial_unit if isinstance(initial_unit, BaseUnit) else initial_unit.base_unit
            queryset = Unit.objects.filter(Q(derivedunit__base_unit=root_unit) | Q(pk=root_unit.pk)).order_by('name')
            dct['unit'] = ModelChoiceField(queryset=queryset, initial=initial_unit.pk, required=True, empty_label=None, widget=UnitWidget)
        #create an hidden field corresponding to the selected parameter
        dct['parameter'] = ModelChoiceField(queryset=parameter.content_type.parameter_set.all(), initial=parameter.pk, required=True, empty_label=None, widget=HiddenInput())
        #generate the model form from a base form and overload properties
        class BaseForm(ModelForm):
            class Meta :
                model = parameter.get_subclass()
                exclude = ['content_type', 'object_id', 'unit']
        form_type = type('MeasurementForm', (BaseForm,), dct)
        return form_type(data, instance=instance, prefix=prefix)

#abstract classes
class Command(object) :
    __metaclass__ = ABCMeta
    
    def __init__(self, receiver):
        self.receiver = receiver
    
    @abstractmethod
    def execute(self):
        return

class Receiver(object) :
    __metaclass__ = ABCMeta
    
    @request_context
    def _create_context(self, form, header, action):
        """Create the context ueseful to display an edition form."""
        context = {
            'form_header':header,
            'background_page':self.request.session['background_page'],
            'cancel_redirect_to':urlresolvers.reverse('editor', args=[self.view_id]), #self.request.session['last_page'],
            'form':form,
            'one_help_text_at_least':one_help_text_at_least(form),
            #'form_style':'parameter_choice_form',
            'action':action
        }
        return context

class ChoiceReceiver(Receiver):
    """
    Convenient base class for ChooseSubclassButton and
    ChooseParameter classes to share the create_form function.
    """
    def create_form(self):
        form = self._create_form_object()
        if form :
            self._update_session(form.__class__)
            return self._dialog_form(form)
        else :
            return self._create_warn_context()

class ChooseSubclassButton(ChoiceReceiver):
    """Generate a form displaying all subclasses of an object type."""
    
    def __init__(self, request, view_id):
        self.request = request
        self.view_id = view_id
        self.node_type = request.GET.get('node_type')
        self.base_class = ContentType.objects.get(pk=int(request.GET.get('class_id'))).model_class()
        subclass_id = request.GET.get('subclass_id', None)
        self.subclasses = [ContentType.objects.get(pk=int(k)) for k in subclass_id.split(',')]
        constraint_id = request.GET.get('constraint_id')
        self.constraint = Constraint.objects.get(pk=int(constraint_id)).cast() if constraint_id else None
        self.form_factory = EditionFormFactory(self.base_class)
    
    def _create_form_object(self) :
        return self.form_factory.createSubclassChoiceForm(self.subclasses, 'form')
    
    def _update_session(self, form_type):
        self.request.session['views'][self.view_id]['edition']['node_id'] = self.request.GET.get('node_id')
        self.request.session['views'][self.view_id]['edition']['parent_node_type'] = self.request.GET.get('parent_node_type')
        if self.node_type == "listoflinks" or self.node_type == "objectlink" or self.node_type == "subclassnode":
            self.request.session['views'][self.view_id]['edition']['parent_class_id'] = self.request.GET.get('parent_class_id')
            self.request.session['views'][self.view_id]['edition']['parent_object_id'] = self.request.GET.get('parent_object_id')
            self.request.session['views'][self.view_id]['edition']['field'] = self.request.GET.get('field')
            self.request.session['views'][self.view_id]['edition']['reverse'] = self.request.GET.get('reverse')
#        if self.node_type == "objectlink" :
#            self.request.session['views'][self.view_id]['edition']['parent_node_type'] = self.request.GET.get('parent_node_type')
        self.request.session['views'][self.view_id]['edition']['constraint'] = self.constraint
        self.request.session['views'][self.view_id]['edition']['base_class'] = self.base_class
        self.request.session.modified = True
    
    @render_to("warn_dialog.html")
    def _create_warn_context(self):
        context = {
            'warn_phrase':"No subclasses of %s available." % self.cls._meta.verbose_name,
            'form_header':"Warning",
            'background_page':self.request.session['background_page'],
            'cancel_redirect_to':urlresolvers.reverse('editor', args=[self.view_id])#self.request.session['last_page'],
        }
        return context
    
    @render_to("dialog_form.html")
    def _dialog_form(self, form):
        return self._create_context(form, "Choose a subclass of %s" % (self.base_class.__name__), urlresolvers.reverse('process-subclasses-form', args=[self.view_id]))

class ChooseParameterButton(ChoiceReceiver):
    """Generate a form displaying all parameters for generic measurements relative to an object type."""
    
    def __init__(self, request, view_id):
        self.request = request
        self.view_id = view_id
        self.node_type = request.GET.get('node_type')
        self.parent_class = ContentType.objects.get(pk=self.request.GET.get('parent_class_id')).model_class()
        #special case when the parent class is subclass of RecordingConfiguration
        if issubclass(self.parent_class, RecordingConfiguration) :
            parent_object = self.parent_class.objects.get(pk=self.request.GET.get('parent_object_id'))
            _cls = parent_object.configuration.cast().__class__
        else :
            _cls = self.parent_class
        self.form_factory = EditionFormFactory(_cls)
    
    def _create_form_object(self) :
        return self.form_factory.createParameterChoiceForm('form')
    
    def _update_session(self, form_type):
        self.request.session['views'][self.view_id]['edition']['node_id'] = self.request.GET.get('node_id')
        self.request.session['views'][self.view_id]['edition']['class_id'] = self.request.GET.get('class_id')
        self.request.session['views'][self.view_id]['edition']['parent_node_type'] = self.request.GET.get('parent_node_type')
        self.request.session['views'][self.view_id]['edition']['parent_class_id'] = self.request.GET.get('parent_class_id')
        self.request.session['views'][self.view_id]['edition']['parent_object_id'] = self.request.GET.get('parent_object_id')
        self.request.session['views'][self.view_id]['edition']['field'] = self.request.GET.get('field')
        self.request.session['views'][self.view_id]['edition']['reverse'] = self.request.GET.get('reverse')
        self.request.session['views'][self.view_id]['edition']['constraint_id'] = self.request.GET.get('constraint_id', None)
        self.request.session.modified = True
    
    @render_to("warn_dialog.html")
    def _create_warn_context(self):
        context = {
            'warn_phrase':"No parameter available for class %s." % self.parent_class._meta.verbose_name,
            'form_header':"Warning",
            'background_page':self.request.session['background_page'],
            'cancel_redirect_to':urlresolvers.reverse('editor', args=[self.view_id])#self.request.session['last_page'],
        }
        return context
    
    @render_to("dialog_form.html")
    def _dialog_form(self, form):
        return self._create_context(form, "Choose a parameter", urlresolvers.reverse('process-parameter-choice-form', args=[self.view_id]))

class SelectParameterButton(Receiver):
    
    def __init__(self, request, view_id):
        self.request = request
        self.view_id = view_id
        self.parameter = Parameter.objects.get(pk=int(request.POST.get('form-parameter')))
        subcls_dct = {
            'B':BoolMeasurement,
            'I':IntegerMeasurement,
            'F':FloatMeasurement,
            'S':StringMeasurement,
        }
        self.form_factory = EditionFormFactory(subcls_dct[self.parameter.type])
    
    def _update_session(self, form_type):
        self.request.session['views'][self.view_id]['edition']['parameter'] = self.parameter
        self.request.session.modified = True
    
    def _create_form_object(self) :
        return self.form_factory.createMeasurementForm(self.parameter, 'form')
    
    @render_to("dialog_form.html")
    def create_form(self):
        form = self._create_form_object()
        self._update_session(form.__class__)
        context = self._create_context(form, "Define %s measurement" % self.parameter, urlresolvers.reverse('validate-add-form', args=[self.view_id]))
        return context

class AddObjectButton(Receiver) :
    
    def __init__(self, request, view_id) :
        self.request = request
        self.view_id = view_id
        self.cls = ContentType.objects.get(pk=int(request.GET.get('class_id'))).model_class()
        constraint_id = request.GET.get('constraint_id')
        self.constraint = Constraint.objects.get(pk=int(constraint_id)).cast() if constraint_id else None
        self.form_factory = EditionFormFactory(self.cls)
        self.form = getattr(self.constraint, 'form', None)
        
    def _create_form_object(self) : 
        return self.form_factory.createGetInsertionForm(self.request.user, 'form', self.form)
    
    def _update_session(self):
        self.request.session['views'][self.view_id]['edition']['class'] = self.cls
        self.request.session['views'][self.view_id]['edition']['constraint'] = self.constraint
        self.request.session.modified = True
    
    @render_to("dialog_form.html")
    def create_form(self):
        form = self._create_form_object()
        context = self._create_context(form, "create a new %s" % (self.cls._meta.verbose_name.lower()), urlresolvers.reverse('validate-add-form', args=[self.view_id]))
        self._update_session()
        return context
         
class ValidateObjectButton(Receiver):
    
    def __init__(self, request, view_id) :
        self.request = request
        self.view_id = view_id
        self.cls = request.session['views'][view_id]['edition']['class']
        self.constraint = request.session['views'][view_id]['edition']['constraint']
        self.instance = request.session['views'][view_id]['edition'].get('instance', None)
        self.form_factory = EditionFormFactory(self.cls)
        self.form = getattr(self.constraint, 'form', None)
        
    def _create_form_object(self) : 
        parent_object = self.request.session['views'][self.view_id]['edition'].get('parent_object', None)
        field_name = self.request.session['views'][self.view_id]['edition'].get('field', None)
        if not self.instance :
            return self.form_factory.createPostInsertionForm(self.request.user, self.request.POST, self.request.FILES, 'form', self.form, parent_object, field_name)
        else :
            return self.form_factory.createPostModifyForm(self.instance, self.request.user, self.request.POST, self.request.FILES, 'form', self.form, parent_object, field_name)
    
    @render_to("dialog_form.html")
    def _resend_form(self, form):
        if hasattr(form, 'instance') :
            url_name = 'validate-modify-form'
            dialog_title = "update an existing %s" % (self.cls._meta.verbose_name.lower())
        else :
            url_name = 'validate-add-form'
            dialog_title = "create a new %s" % (self.cls._meta.verbose_name.lower())
        context = self._create_context(form, dialog_title, urlresolvers.reverse(url_name, args=[self.view_id]))
        return context
            
    def save_form(self):
        form = self._create_form_object()
        if not form.is_valid() :
            return self._resend_form(form)
        else :
            self.form_factory._cast_links(form)
            instance = form.save()
            if UnderAccessControlEntity.objects.is_registered(instance.__class__) :
                Permission.objects.create_default_permissions(instance, self.request.user)
            else :
                ObjectIndex.objects.register_object(instance)
            return HttpResponseRedirect(self.request.session['last_page'])
            
class ValidateMeasurementModificationButton(ValidateObjectButton):
    
    def _create_form_object(self) :
        parameter = Parameter.objects.get(pk=int(self.request.POST.get('form-parameter')))
        return self.form_factory.createMeasurementForm(parameter, 'form', data=self.request.POST, instance=self.instance)

class AddObjectThenLinkButton(AddObjectButton):
    
    def __init__(self, request, view_id):
        super(AddObjectThenLinkButton, self).__init__(request, view_id)
        self.parent_class = ContentType.objects.get(pk=int(request.GET.get('parent_class_id'))).model_class()
        object_id = request.GET.get('parent_object_id')
        self.field = request.GET.get('field')
        self.reverse = bool(int(request.GET.get('reverse')))
        try :
            self.parent_object = self.parent_class.objects.get(pk=int(object_id))
        except :
            self.parent_object = self.parent_class.objects.get(pk=object_id)
    
    def _create_form_object(self) :
        return self.form_factory.createGetInsertionForm(self.request.user, 'form', self.form, self.parent_object, self.field)
    
    def _update_session(self):
        self.request.session['views'][self.view_id]['edition']['class'] = self.cls 
        self.request.session['views'][self.view_id]['edition']['constraint'] = self.constraint
        self.request.session['views'][self.view_id]['edition']['parent_object'] = self.parent_object
        self.request.session['views'][self.view_id]['edition']['field'] = self.field 
        self.request.session['views'][self.view_id]['edition']['reverse'] = self.reverse
        self.request.session.modified = True

class AddMeasurementButton(AddObjectThenLinkButton):
    
    def __init__(self, request, view_id):
        super(AddMeasurementButton, self).__init__(request, view_id)
        self.parameter = Parameter.objects.get(pk=int(self.request.GET.get('parameter_id')))
    
    def _create_form_object(self):
        return self.form_factory.createMeasurementForm(self.parameter, 'form')

class ValidateObjectThenLinkButton(ValidateObjectButton):
    
    def __init__(self, request, view_id) :
        super(ValidateObjectThenLinkButton, self).__init__(request, view_id)
        self.parent_object = request.session['views'][view_id]['edition']['parent_object']
        self.field = request.session['views'][view_id]['edition']['field']
        self.node_type = request.session['views'][view_id]['edition']['node_type']
        self.reverse = request.session['views'][view_id]['edition']['reverse']
    
    def _create_form_object(self) :
        return self.form_factory.createPostInsertionForm(self.request.user, self.request.POST, self.request.FILES, 'form', self.form, self.parent_object, self.field)

    @render_to("dialog_form.html")
    def _resend_form(self, form):
        return self._create_context(form, "create a new %s" % (self.cls._meta.verbose_name.lower()), urlresolvers.reverse('validate-add-form', args=[self.view_id]))

    def save_form(self):
        form = self._create_form_object()
        if not form.is_valid() :
            return self._resend_form(form)
        else :
            self.form_factory._cast_links(form)
            commit = False
            instance = form.save(commit=commit)
            is_fake = is_fake_object_link(self.node_type, self.parent_object.__class__, self.field)
            if self.node_type == "objectlink" and not is_fake :
                if self.reverse :
                    field = self.parent_object.__class__._meta.get_field_by_name(instance.__class__.__name__.lower())[0].field.name
                    setattr(instance, field, self.parent_object)
                    instance.save()
                else :
                    instance.save()
                    setattr(self.parent_object, self.field, instance)
                    self.parent_object.save()     
            elif self.node_type == "listoflinks" or self.node_type == "subclassnode" or is_fake :
                if not isinstance(instance, (Permission, Tag)) :
                    attr = getattr(self.parent_object, self.field)
                    if attr.__class__.__name__ == 'ManyRelatedManager' :
                        instance.save()
                    if (attr.__class__.__name__ == 'ManyRelatedManager') and attr.through :
                        dct = dict()
                        through_fields = [k for k in get_all_fields(attr.through) if isinstance(k, ForeignKey)]
                        assert len(through_fields) == 2, "problem with through = %s fields" % attr.through 
                        for field in through_fields :
                            if isinstance(instance, self.parent_object.__class__) :
                                dct[field.name] = instance if self.field.startswith(field.name) else self.parent_object
                            else :
                                dct[field.name] = instance if isinstance(instance, field.rel.to) else self.parent_object
                        cls = attr.through.objects.create(**dct)  
                    else :
                        attr.add(instance)
                else :
                    #link the permission or tag to 
                    #the content type object relative to the parent object
                    registered = ObjectIndex.objects.get_registered_object(self.parent_object)
                    if  isinstance(instance, Permission) :
                        instance.index = registered
                        instance.save()
                    else :
                        instance.save()
                        instance.indices.add(registered)
                    
            else :
                raise NotImplementedError()
            form.save_m2m()
            #create default permission on an object
            #register an object as a content type object
            if UnderAccessControlEntity.objects.is_registered(instance.__class__) :
                Permission.objects.create_default_permissions(instance, self.request.user)
            else :
                ObjectIndex.objects.register_object(instance)
            return HttpResponseRedirect(self.request.session['last_page'])

class ValidateMeasurementThenLinkButton(ValidateObjectThenLinkButton):

    def _create_form_object(self) :
        parameter = Parameter.objects.get(pk=int(self.request.POST.get('form-parameter')))
        return self.form_factory.createMeasurementForm(parameter, 'form', self.request.POST)

class ModifyObjectButton(AddObjectButton) :
    
    def __init__(self, request, view_id) :
        super(ModifyObjectButton, self).__init__(request, view_id)
        #object
        object_id = request.GET.get('object_id')
        try : 
            instance = self.cls.objects.get(pk=int(object_id))
        except :
            instance = self.cls.objects.get(pk=object_id)
        self.instance = instance
        #parent object
        self.field = request.GET.get('field', None)
        parent_class_id = request.GET.get('parent_class_id', None)
        if parent_class_id :
            parent_class = ContentType.objects.get(pk=int(parent_class_id)).model_class()
            object_id = request.GET.get('parent_object_id')
            try :
                self.parent_object = parent_class.objects.get(pk=int(object_id))
            except :
                self.parent_object = parent_class.objects.get(pk=object_id)
        else :
            self.parent_object = None
        
    def _create_form_object(self) : 
        return self.form_factory.createGetModifyForm(self.instance, self.request.user, 'form', self.form, self.parent_object, self.field)
    
    def _update_session(self):
        self.request.session['views'][self.view_id]['edition']['class'] = self.cls
        self.request.session['views'][self.view_id]['edition']['constraint'] = self.constraint
        self.request.session['views'][self.view_id]['edition']['instance'] = self.instance
        self.request.session['views'][self.view_id]['edition']['parent_object'] = self.parent_object
        self.request.session['views'][self.view_id]['edition']['field'] = self.field
        self.request.session.modified = True
    
    @render_to("dialog_form.html")
    def create_form(self):
        form = self._create_form_object()
        context = self._create_context(form, "update an existing %s" % (self.cls._meta.verbose_name.lower()), urlresolvers.reverse('validate-modify-form', args=[self.view_id]))
        self._update_session()
        return context

class ModifyMeasurementButton(ModifyObjectButton):
    
    def _create_form_object(self):
        return self.form_factory.createMeasurementForm(self.instance.parameter, 'form', instance=self.instance)
    
class ManageLinkButton(Receiver):
    
    def __init__(self, request, view_id):
        self.request = request
        self.view_id = view_id
        self.node_type = request.GET.get('node_type')
        self.cls = ContentType.objects.get(pk=int(request.GET.get('class_id'))).model_class()
        parent_class = ContentType.objects.get(pk=int(request.GET.get('parent_class_id'))).model_class()
        object_id = request.GET.get('parent_object_id')
        try :
            parent_object = parent_class.objects.get(pk=int(object_id))
        except :
            parent_object = parent_class.objects.get(pk=object_id)  
        self.parent_object = ObjectIndex.objects.get_registered_object(parent_object) if issubclass(self.cls, (Permission, Tag)) else parent_object  
        self.field = request.GET.get('field')
        self.reverse = bool(int(request.GET.get('reverse')))

class UnlinkButton(ManageLinkButton):
    __metaclass__ = ABCMeta
    
    def __init__(self, request, view_id):
        super(UnlinkButton, self).__init__(request, view_id)
        self.parent_node_type = request.GET.get('parent_node_type')
    
    @abstractmethod
    def unlink(self):
        return
    
    def _remove(self, instance):
        attr = getattr(self.parent_object, self.field)
        attr.remove(instance)
    
class UnlinkObjectButton(UnlinkButton):
    
    def __init__(self, request, view_id):
        super(UnlinkObjectButton, self).__init__(request, view_id)
        object_id = request.GET.get('object_id')
        try : 
            self.instance = self.cls.objects.get(pk=int(object_id))
        except :
            self.instance = self.cls.objects.get(pk=object_id)
        
    def _unlink_forward(self):
        setattr(self.parent_object, self.field, None)
        self.parent_object.save()

    def _unlink_backward(self, instance):
        field = self.parent_object.__class__._meta.get_field_by_name(instance.__class__.__name__.lower())[0].field.name
        setattr(instance, field, None)
        instance.save()

    def unlink(self):
        """Dispatch unlink actions."""
        is_fake = is_fake_object_link(self.node_type, self.parent_object.__class__, self.field)
        if self.parent_node_type == 'listoflinks' or self.parent_node_type == 'subclassnode' or is_fake :
            self._remove(self.instance)
        elif self.parent_node_type in ['objectlink', 'objectnode'] :
            if self.reverse :
                self._unlink_backward(self.instance)
            else :
                self._unlink_forward()
        else :
            raise NotImplementedError(self.parent_node_type)
        return HttpResponseRedirect(self.request.session['last_page']) 

class UnlinkObjectsButton(UnlinkButton):
    
    def __init__(self, instances, parent_object, field, parent_node_type, reverse):
        super(UnlinkObjectsButton, self).__init__(parent_object, field, parent_node_type, reverse)
        self.instances = instances

    def unlink(self):
        """Dispatch unlink actions."""
        if self.parent_node_type == 'listoflinks' or self.parent_node_type == 'subclassnode':
            for instance in self.instances :
                self._remove(instance)
        else :
            raise NotImplementedError(self.parent_node_type)

class ChooseObjectButton(ManageLinkButton):
    
    def __init__(self, request, view_id):
        super(ChooseObjectButton, self).__init__(request, view_id)
        self.node_type = request.GET.get('node_type')
        self.form_factory = EditionFormFactory(self.cls)
    
    def _filter_queryset(self, queryset):
        #in a hierarchical structure case, avoid cyclic references
        if (self.cls == self.parent_object.__class__) :
            queryset = queryset.exclude(pk=self.parent_object.pk)
            if isinstance(self.parent_object, HierarchicalStructure) :
                parent_pks = [k.pk for k in self.parent_object.get_parents()]
                children_pks = [k.pk for k in self.parent_object.get_children(recursive=True)]
                queryset = queryset.exclude(pk__in=parent_pks).exclude(pk__in=children_pks)
        #display only accessible objects
        if UnderAccessControlEntity.objects.is_registered(self.cls) :
            proxy_user = User.objects.get(pk=self.request.user.pk)
            queryset = proxy_user.get_accessible(queryset)
        return queryset
    
    def _update_session(self, queryset):
        self.request.session['views'][self.view_id]['edition']['class'] = self.cls 
        self.request.session['views'][self.view_id]['edition']['parent_object'] = self.parent_object
        self.request.session['views'][self.view_id]['edition']['field'] = self.field 
        self.request.session['views'][self.view_id]['edition']['reverse'] = self.reverse
        self.request.session['views'][self.view_id]['edition']['queryset'] = queryset
        self.request.session['views'][self.view_id]['edition']['node_type'] = self.node_type
        self.request.session.modified = True
    
    @render_to("warn_dialog.html")
    def _create_warn_context(self):
        context = {
            'warn_phrase':"No %s available." % self.cls._meta.verbose_name,
            'form_header':"Warning",
            'background_page':self.request.session['background_page'],
            'cancel_redirect_to':urlresolvers.reverse('editor', args=[self.view_id]), #self.request.session['last_page'],
        }
        return context

    def _update_queryset(self):
        """Get interesting and available objects.""" 
        queryset = self._get_base_queryset()
        return self._filter_queryset(queryset)
    
    def create_form(self):
        queryset = self._update_queryset()
        self._update_session(queryset)
        if queryset :
            form = self._create_form_object(queryset)
            return self._dialog_form(form)
        else :
            return self._create_warn_context()

class ChooseSingleObjectButton(ChooseObjectButton):    
    
    def _get_base_queryset(self):
        return self.cls.objects.all()
    
    @render_to("dialog_form.html")
    def _dialog_form(self, form):
        return self._create_context(form, "Choose an existing %s" % (self.cls._meta.verbose_name.lower()), urlresolvers.reverse('validate-link-form', args=[self.view_id]))
    
    def _create_form_object(self, queryset):
        return self.form_factory.createSingleObjectChoiceForm(queryset)
        
class ChooseSeveralObjectsButton(ChooseObjectButton):
    
    def _get_base_queryset(self):
        #avoid display already linked objects
        return self.cls.objects.exclude(pk__in=[k.pk for k in getattr(self.parent_object, self.field).all()])
    
    @render_to("dialog_form.html")
    def _dialog_form(self, form):
        return self._create_context(form, "Choose existing %s" % (self.cls._meta.verbose_name_plural.lower()), urlresolvers.reverse('validate-link-form', args=[self.view_id]))
    
    def _create_form_object(self, queryset):
        return self.form_factory.createSeveralObjectsChoiceForm(queryset)
  
class ValidateLinkButton(Receiver):
    
    def __init__(self, request, view_id):
        self.request = request
        self.view_id = view_id
        self.cls = self.request.session['views'][self.view_id]['edition']['class']
        self.parent_object = self.request.session['views'][self.view_id]['edition']['parent_object']
        self.field = self.request.session['views'][self.view_id]['edition']['field']
        self.node_type = self.request.session['views'][self.view_id]['edition']['node_type']
        self.reverse = self.request.session['views'][self.view_id]['edition']['reverse']
        self.queryset = self.request.session['views'][self.view_id]['edition']['queryset']
        self.form_factory = EditionFormFactory(self.cls)
    
    def _get_instances(self):
        key = 'List of %s' % (self.cls._meta.verbose_name_plural.lower())
        if self.node_type == 'listoflinks' or self.node_type == 'subclassnode' :
            form = self.form_factory.createSeveralObjectsChoiceForm(self.queryset, post=self.request.POST)
            if form.is_valid():
                instances = form.cleaned_data[key]
        elif self.node_type == 'objectlink' :
            form = self.form_factory.createSingleObjectChoiceForm(self.queryset, post=self.request.POST)
            if form.is_valid():
                instances = [form.cleaned_data[key]]
        else :
            raise NotImplementedError()
        return instances
    
    def _link_forward(self, instances):
        for instance in instances :
            setattr(self.parent_object, self.field, instance)
            self.parent_object.save()
    
    def _link_backward(self, instances):
        field = self.parent_object.__class__._meta.get_field_by_name(self.cls.__name__.lower())[0].field.name
        for instance in instances :
            setattr(instance, field, self.parent_object)
            instance.save()
    
    def _add(self, instances):
        attr = getattr(self.parent_object, self.field)
        for instance in instances :
            attr.add(instance)
    
    def link(self):
        """Dispatch linking actions."""
        instances = self._get_instances()
        is_fake = is_fake_object_link(self.node_type, self.parent_object.__class__, self.field)
        if self.node_type == 'listoflinks' or self.node_type == 'subclassnode' or is_fake :
            self._add(instances)
        elif self.node_type == 'objectlink' :
            if self.reverse :
                self._link_backward(instances)
            else :
                self._link_forward(instances)
        else :
            raise NotImplementedError(self.link)
        return HttpResponseRedirect(self.request.session['last_page']) 

class DeleteObjectButton(Receiver):
    #django delete() function automatically delete objects depending on the object to delete
    #that's why it is necessary to warn the user of this kind of cascading mechanism
    #and to offer to him the choice to delete or not depending objects 
    #when the corresponding field is not required in the foreign object
    
    def __init__(self, request, view_id):
        self.request = request
        self.view_id = view_id
        self.cls = ContentType.objects.get(pk=int(request.GET.get('class_id'))).model_class()
        object_id = request.GET.get('object_id')
        try : 
            instance = self.cls.objects.get(pk=int(object_id))
        except :
            instance = self.cls.objects.get(pk=object_id)
        self.instance = instance
        self.dependencies = get_all_dependencies(self.instance)
        self.cascaded = [k for k in self.dependencies if k[2]]
        self.links = get_all_links(self.instance)
    
    @request_context
    def _create_context(self, header, action):
        context = {
            'class_name':self.cls._meta.verbose_name.lower(),
            'form_header':header,
            'background_page':self.request.session['background_page'],
            'cancel_redirect_to':urlresolvers.reverse('editor', args=[self.view_id]), #self.request.session['last_page'],
            'object':self.instance,
            'depending_objects':self.dependencies,
            'cascaded_objects':self.cascaded,
            'm2m_links':self.links,
            'action':action
        }
        return context
    
    def _update_session(self):
        self.request.session['views'][self.view_id]['edition']['dependencies'] = self.dependencies
        self.request.session['views'][self.view_id]['edition']['object'] = self.instance
        self.request.session.modified = True
    
    @render_to("delete_form.html")
    def create_form(self):
        self._update_session()
        context = self._create_context('Delete selected %s' % (self.cls._meta.verbose_name.lower()), urlresolvers.reverse('validate-delete-form', args=[self.view_id]))
        return context

class ValidateDeleteButton(Receiver):
    
    def __init__(self, request, view_id):
        self.request = request
        self.delete_all = request.POST.get('delete_all', False)
        self.selection = request.POST.getlist('selected_objects') if not self.delete_all else None
        self.dependencies = request.session['views'][view_id]['edition']['dependencies']
        self.instance = request.session['views'][view_id]['edition']['object']
    
    def delete(self):
        all_objects = [k[1] for k in self.dependencies]
        if not self.delete_all :
            selected_objects = [k for k in all_objects if "%s.%s" % (k.__class__.__name__, k.pk) in self.selection]
        else :
            selected_objects = all_objects
        secure_delete(self.instance, self.request.user, selected_objects, filter=True)
        return HttpResponseRedirect(self.request.session['last_page'])

class CancelButton(Receiver):
    
    def redirect(self) :
        pass

class DisplayForm(Command):
    """Display a Form."""
    
    def execute(self):
        return self.receiver.create_form()

class CommitObjectToDatabase(Command):
    """Commit changes to the database."""
     
    def execute(self):
        return self.receiver.save_form()

class RemoveObjectFromDatabase(Command):
    """Remove an object from the database."""
    
    def execute(self):
        return self.receiver.delete()

class UnlinkObject(Command):
    """Remove link existing between two objects."""
    
    def execute(self):
        return self.receiver.unlink()

class LinkObject(Command):
    
    def execute(self):
        return self.receiver.link()

#modifying object
class DisplayDialogBeforeDelete(Command):
    """Display a dialog to validate the deletion of an object."""
    
    def execute(self):
        pass

class ChooseSubclassBeforeInsertionForm(Command):
    
    def execute(self):
        pass
