#encoding:utf-8
from django.conf import settings
from django.forms import Form, ModelMultipleChoiceField, ModelChoiceField
from helmholtz.access_control.models import UnderAccessControlEntity, User
import helmholtz.editor.forms as admin_forms

class FormGenerator(object) :

    def __init__(self, action, view_id, form_type=None, request=None, form_object=None, parent_object=None, after_class_selection=False) :
        self.request = request
        self.proxy_user = User.objects.get(pk=self.request.user)
        self.action = action
        self.view_id = view_id
        self.form_object = form_object
        self.parent_object = parent_object
        self.form_type = form_type         
        self.form = getattr(admin_forms, self.form_type)
        self.after_class_selection = after_class_selection

    def create(self):
        if (self.request.method != 'POST') or ((self.request.method == 'POST') and self.after_class_selection) :
            #change dynamically model choice fields
            #in order to display only data accessible to the user
            for field in self.form.base_fields :
                field_obj = self.form.base_fields[field]
                if (isinstance(field_obj, ModelMultipleChoiceField) or isinstance(field_obj, ModelChoiceField)) and UnderAccessControlEntity.objects.is_registered(field_obj.queryset.model) :
                    field_obj.queryset = self.proxy_user.get_accessible(field_obj.queryset)
            if self.action == 'add_object' : 
                form_obj = self.form(prefix="%s_form" % (self.view_id))
            if self.action == 'modify_object' :  
                form_obj = self.form(instance=self.form_object, prefix="%s_form" % (self.view_id))
            else :
                pass
        else :
            if self.action == 'add_object' :
                form_obj = self.form(self.request.POST, self.request.FILES, prefix="%s_form" % (self.view_id))
            elif self.action == 'modify_object' :
                form_obj = self.form(self.request.POST, self.request.FILES, instance=self.form_object, prefix="%s_form" % (self.view_id))
            else :
                pass
        #textarea widgets from a model specifies automatic cols and rows
        for field in form_obj.fields :
            if form_obj.fields[field].__class__.__name__ in ['ImageField', 'CharField', 'PhysicalQuantityField'] :
                
                if form_obj.fields[field].widget.__class__.__name__ in ['Textarea', 'PasswordInput'] :
                    if form_obj.fields[field].widget.attrs.has_key("cols") :
                        form_obj.fields[field].widget.attrs.pop("cols")
                    if form_obj.fields[field].widget.attrs.has_key("rows") :
                        form_obj.fields[field].widget.attrs['rows'] = 1#.pop("rows")    
        return form_obj 
    
    def initialize_static_form(self) :
        """As Dojo TimeField requires isoformat THH:MM:SS, it is necessary to adapt the initial value coming from the server."""
        obj = self.find_object()
        form_obj = self.form(instance=obj, prefix=self.type)   
        return form_obj
    
    def initialize_form(self) :
        if (self.id == None) and (self.request.method != 'POST') : #generation pour un objet qui n'existe pas encore
            form_obj = self.form(prefix="%s_form" % (self.view_id))
        elif (self.id == None) and (self.request.method == 'POST') : #generation pour un formulaire invalide
            form_obj = self.form(self.request.POST, self.request.FILES, prefix="%s_form" % (self.view_id))
        elif (self.id != None) and (self.request.method != 'POST') :
            obj = self.find_object()
            form_obj = self.form(instance=obj, prefix="%s_form" % (self.view_id))
        elif (self.id != None) and (self.request.method == 'POST') :
            obj = self.find_object()
            form_obj = self.form(self.request.POST, self.request.FILES, instance=obj, prefix="%s_form" % (self.view_id))
        return form_obj
