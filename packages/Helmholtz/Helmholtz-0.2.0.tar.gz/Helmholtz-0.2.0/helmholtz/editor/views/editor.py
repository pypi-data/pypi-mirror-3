#encoding:utf-8
from django.db.models import signals
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType 
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page
from helmholtz.measurements.models import Parameter, GenericMeasurement
from helmholtz.editor.shortcuts import get_schema, get_constraint
from helmholtz.editor.view import View
from helmholtz.editor.commands import AddObjectButton, \
                                      AddObjectThenLinkButton, \
                                      ModifyObjectButton, \
                                      UnlinkObjectButton, \
                                      DeleteObjectButton, \
                                      ValidateObjectButton, \
                                      ValidateObjectThenLinkButton, \
                                      ValidateLinkButton, \
                                      ValidateDeleteButton, \
                                      ChooseSeveralObjectsButton, \
                                      ChooseSingleObjectButton, \
                                      ChooseSubclassButton, \
                                      ChooseParameterButton, \
                                      AddMeasurementButton, \
                                      ModifyMeasurementButton, \
                                      ValidateMeasurementThenLinkButton, \
                                      ValidateMeasurementModificationButton, \
                                      DisplayForm, \
                                      CommitObjectToDatabase, \
                                      UnlinkObject, \
                                      LinkObject, \
                                      RemoveObjectFromDatabase                                 

view = View('administration')

def reset_view(sender, **kwargs):
    global view
    if kwargs['instance'].__module__ == 'helmholtz.editor.models' :
        view = View('administration')

# reset the View when it is 
# changed from the web browser
signals.post_delete.connect(reset_view)
signals.post_save.connect(reset_view)

def detail(node):
    """Execute recursively detail for test purpose."""
    nodes = node.detail()
    for _node in nodes :
        if hasattr(_node, 'detail') and callable(_node.detail) :
            detail(_node)
        else :
            break
    return

def test_recursion(condition):
    """Test for recursion."""
    def renderer(func):
        def wrapper(request, *args, **kwargs):
            if condition :
                global view
                detail(view)
            return func(request, *args, **kwargs)    
        return wrapper
    return renderer

def update_view_from_last_state(view_func):
    """
    Update the editor widget internal state from the request after a user action.
    Separate the editor widget internal state update from its display.
    """
    def modified_function(request, *args, **kwargs):
        global view
        view.update_from_last_state(request)
        return view_func(request, *args, **kwargs)
    modified_function.__doc__ = view_func.__doc__
    return modified_function

@login_required
def init_session_for_editor(request, view_id):
    """Init the session to store editor states."""
    #create a placeholder to store view widgets and their states into the session
    if not request.session.has_key('views') or request.GET.get('reset', False) :
        request.session['views'] = SortedDict()
        request.session.modified = True
    if not request.session['views'].has_key(view_id) or request.GET.get('reset', False) :
        request.session['views'][view_id] = SortedDict()
        request.session['views'][view_id]['states'] = SortedDict()
        request.session['views'][view_id]['ordering'] = SortedDict()
        request.session['views'][view_id]['order_by'] = SortedDict()
        request.session['views'][view_id]['pages'] = SortedDict()
        request.session['views'][view_id]['selected_class_node'] = None
        request.session['views'][view_id]['edition'] = SortedDict()
        request.session.modified = True
    #redirect to the editor page  
    redirection = urlresolvers.reverse('editor', args=[view_id])
    return HttpResponseRedirect(redirection)

@memorise_last_page
@memorise_last_rendered_page
@login_required
def execute_command(request, view_id):
    """Update editor state from user actions."""
    action = request.GET.get('action', None)
    if action :
        node_id = str(request.GET.get('node_id', None))
        if action == "open" :
            request.session['views'][view_id]['states'][node_id] = True
        elif action == "close" :
            request.session['views'][view_id]['states'][node_id] = False
        elif action == 'sort_table' :
            request.session['views'][view_id]['ordering'][node_id] = request.GET.get('ordering')
            request.session['views'][view_id]['order_by'][node_id] = request.GET.get('order_by')
        elif action == 'select_page' :
            page = int(request.GET.get('page'))
            request.session['views'][view_id]['pages'][node_id] = page
        elif action == 'select_class' :
            request.session['views'][view_id]['selected_class_node'] = node_id
        request.session.modified = True
    #redirect to the editor page after an action
    redirection = urlresolvers.reverse('editor', args=[view_id])
    return HttpResponseRedirect(redirection)

@update_view_from_last_state
@test_recursion(False)
@memorise_last_page
@memorise_last_rendered_page
@login_required
def display_view(request, view_id):
    """Display the current state of the editor widget."""
    global view
    context = {'view':view, 'request_user':request.user, 'enable_scroll_position':True}
    r_context = RequestContext(request, context)
    response = render_to_response("editor.html", r_context)
    return response

def reset_session(request, view_id, node_type, action):
    """Reset editor session placeholder."""
    request.session['views'][view_id]['edition'] = SortedDict()
    request.session['views'][view_id]['edition']['action'] = action
    request.session['views'][view_id]['edition']['node_type'] = node_type

def set_command(request, view_id, receiver_type, command_type):
    """Return a Command bound to a Receiver."""
    receiver = receiver_type(request, view_id)
    command = command_type(receiver)
    return command

def process_subclasses_form(request, view_id):
    """
    Process the form relative to the user subclass choice.
    """
    action = request.session['views'][view_id]['edition']['action']
    node_type = request.session['views'][view_id]['edition']['node_type']
    node_id = request.session['views'][view_id]['edition']['node_id']
    base_class = request.session['views'][view_id]['edition']['base_class']
    subclass_id = int(request.POST.get('form-%s type' % (base_class.__name__)))
    parameters = "?node_type=%s&node_id=%s&class_id=%s" % (node_type, node_id, subclass_id)
    subclass_ct = ContentType.objects.get(pk=subclass_id)
    parent_constraint = request.session['views'][view_id]['edition']['constraint']
    
    #get the constraint from the parent one
    constraint = None
    if subclass_ct.model_class() == base_class :
        constraint = parent_constraint
    elif parent_constraint :
        schema = get_schema(parent_constraint.entity, subclass_ct.model_class())
        constraint = get_constraint(schema)
    
    #complete list of parameters with the constraint id
    if constraint :
        parameters += "&constraint_id=%s" % (constraint.pk)

    #complete list of parameters with parent and field properties
    if node_type == 'listoflinks'  or node_type == 'objectlink' :
        parent_link = request.session['views'][view_id]['edition']['parent_node_type']
        parent_class_id = request.session['views'][view_id]['edition']['parent_class_id']
        parent_object_id = request.session['views'][view_id]['edition']['parent_object_id']
        field = request.session['views'][view_id]['edition']['field']
        reverse = request.session['views'][view_id]['edition']['reverse']
        parameters += "&parent_node_type=%s&parent_class_id=%s&parent_object_id=%s&field=%s&reverse=%s" % (parent_link, parent_class_id, parent_object_id, field, reverse)

    redirection = urlresolvers.reverse('get-%s-form' % action, args=[view_id]) + parameters
    return HttpResponseRedirect(redirection)

def process_parameter_choice_form(request, view_id):
    """
    Process the form relative to the user measurement parameter choice.
    """
    action = request.session['views'][view_id]['edition']['action']
    node_type = request.session['views'][view_id]['edition']['node_type']
    node_id = request.session['views'][view_id]['edition']['node_id']
    #retrieve the selected parameter
    parameter = Parameter.objects.get(pk=int(request.POST.get('form-parameter')))
    #get the actual subclass of GenericMeasurement
    subcls = ContentType.objects.get_for_model(parameter.get_subclass())
    parameters = "?node_type=%s&node_id=%s&class_id=%s" % (node_type, node_id, subcls.pk)
    #complete list of parameters with constraint id
    constraint_id = request.session['views'][view_id]['edition'].get('constraint_id')
    if constraint_id :
        parameters += "&constraint_id=%s" % (constraint_id)
    #complete list of parameters with parent and field properties
    parent_link = request.session['views'][view_id]['edition']['parent_node_type']
    parent_class_id = request.session['views'][view_id]['edition']['parent_class_id']
    parent_object_id = request.session['views'][view_id]['edition']['parent_object_id']
    field = request.session['views'][view_id]['edition']['field']
    reverse = request.session['views'][view_id]['edition']['reverse']
    parameters += "&parent_node_type=%s&parent_class_id=%s&parent_object_id=%s&field=%s&reverse=%s&parameter_id=%s" % (parent_link, parent_class_id, parent_object_id, field, reverse, parameter.pk)
    redirection = urlresolvers.reverse('get-%s-form' % action, args=[view_id]) + parameters
    return HttpResponseRedirect(redirection)

def get_add_form(request, view_id):
    """Create a form to add a new object in the database."""
    node_type = request.GET.get('node_type')
    class_id = request.GET.get('class_id')
    cls = ContentType.objects.get_for_id(int(class_id)).model_class()
    subclass_id = request.GET.get('subclass_id', None)
    reset_session(request, view_id, node_type, 'add')
    if issubclass(cls, GenericMeasurement) :
        parameter_id = request.GET.get('parameter_id', None)
        if not parameter_id :
            receiver_type = ChooseParameterButton
        else :
            receiver_type = AddMeasurementButton
    else :
        if not subclass_id :
            if node_type == 'classnode' :
                receiver_type = AddObjectButton
            elif node_type == 'listoflinks' or node_type == 'objectlink' or node_type == 'subclassnode' :
                receiver_type = AddObjectThenLinkButton
            else :
                raise NotImplementedError()
        else :
            receiver_type = ChooseSubclassButton   
    command = set_command(request, view_id, receiver_type, DisplayForm)
    return command.execute()

def validate_add_form(request, view_id):
    """Process form data corresponding to the new object."""
    node_type = request.session['views'][view_id]['edition']['node_type']
    cls = request.session['views'][view_id]['edition']['class']
    if node_type == 'classnode' :
        receiver_type = ValidateObjectButton
    elif node_type == 'listoflinks' or node_type == 'objectlink' or node_type == 'subclassnode' :
        if issubclass(cls, GenericMeasurement) :
            receiver_type = ValidateMeasurementThenLinkButton
        else :
            receiver_type = ValidateObjectThenLinkButton
    else :
        raise NotImplementedError()
    command = set_command(request, view_id, receiver_type, CommitObjectToDatabase)
    return command.execute()

def get_modify_form(request, view_id):
    """Create a form to modify a database object.""" 
    node_type = request.GET.get('node_type')
    reset_session(request, view_id, node_type, 'modify')
    class_id = request.GET.get('class_id')
    cls = ContentType.objects.get_for_id(int(class_id)).model_class()
    if issubclass(cls, GenericMeasurement) :
        receiver_type = ModifyMeasurementButton
    else :
        receiver_type = ModifyObjectButton
    command = set_command(request, view_id, receiver_type, DisplayForm)
    return command.execute()

def validate_modify_form(request, view_id):
    """Update a database object from the posted form."""
    cls = request.session['views'][view_id]['edition']['class']
    if issubclass(cls, GenericMeasurement) :
        receiver_type = ValidateMeasurementModificationButton
    else :
        receiver_type = ValidateObjectButton
    command = set_command(request, view_id, receiver_type, CommitObjectToDatabase)
    return command.execute()

def get_delete_form(request, view_id):
    node_type = request.GET.get('node_type')
    reset_session(request, view_id, node_type, 'delete')
    command = set_command(request, view_id, DeleteObjectButton, DisplayForm)
    return command.execute()

def validate_delete_form(request, view_id):
    command = set_command(request, view_id, ValidateDeleteButton, RemoveObjectFromDatabase)
    return command.execute()

def unlink_object(request, view_id):
    node_type = request.GET.get('node_type')
    reset_session(request, view_id, node_type, 'unlink')
    command = set_command(request, view_id, UnlinkObjectButton, UnlinkObject)
    return command.execute()

def link_object(request, view_id):
    node_type = request.GET.get('node_type')
    subclass_id = request.GET.get('subclass_id', None)
    reset_session(request, view_id, node_type, 'link')
    if not subclass_id :
        if node_type == 'listoflinks' or node_type == 'subclassnode' :
            receiver_type = ChooseSeveralObjectsButton
        elif node_type == 'objectlink' :
            receiver_type = ChooseSingleObjectButton
        else :
            raise NotImplementedError()
    else :
        receiver_type = ChooseSubclassButton
    command = set_command(request, view_id, receiver_type, DisplayForm)
    return command.execute()

def validate_link_form(request, view_id):
    command = set_command(request, view_id, ValidateLinkButton, LinkObject)
    return command.execute()

def get_tag_form(request, view_id):
    raise NotImplementedError()

def process_action(request, view_id):
    raise NotImplementedError()
