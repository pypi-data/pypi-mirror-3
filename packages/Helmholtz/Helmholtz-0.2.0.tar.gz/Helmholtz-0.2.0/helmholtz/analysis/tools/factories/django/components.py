from helmholtz.analysis.tools.components import Component
from helmholtz.analysis.models.components import Component as ModelComponent

class ComponentFactory(ObjectFactory) :
    """Automatic Component Generation. Make a component from one stored into the database."""
    
    def __init__(self, type, execute=None) :
        self.model = ModelComponent.objects.get(pk=type)#, base=False)#cannot create a base component
        self.comptype = type
        self.execute = execute
    
    def update_pin_members(self, queryset, members) :
        for pin in queryset :
            pin_type = eval(pin.pintype.pk) 
            members.update({pin.name : pin_type(constraint=pin.constraint, usecase=pin.usecase)})
    
    def add_pin_members(self, members) :
        pins = self.model.pin_set
        inputs = pins.filter(pintype="Input")
        parameters = pins.filter(pintype="Parameter")
        outputs = pins.filter(pintype="Output")
        self.update_pin_members(inputs, members)
        self.update_pin_members(outputs, members)
        self.update_pin_members(parameters, members)
    
    def import_component(self, component, members) :
        exec("from %s import %s" % (component.subcomponent_id.package, component.subcomponent_id.pk))
        exec("cls = %s" % (component.subcomponent_id.pk))
        members.update({component.alias : cls()})
    
    def add_component_members(self, members) :
        subcomponents = self.model.component
        for component in subcomponents.filter(subcomponent_id__base=True) :
            self.import_component(component, members)
        for component in subcomponents.filter(subcomponent_id__base=False) :
            factory = ComponentFactory(component.subcomponent_id.pk)
            subcomponent = factory.create_component()
            members.update({component.alias : subcomponent})
    
    def add_connections(self, instance) :
        connections = self.model.connection_set
        for connection in connections.all() : 
            if connection.alias_left :
                component_left = getattr(instance, connection.alias_left.alias)
            else :
                component_left = instance
            if connection.alias_right :
                component_right = getattr(instance, connection.alias_right.alias)
            else :
                component_right = instance
            pin_left = getattr(component_left, connection.pin_left.name)
            pin_right = getattr(component_right, connection.pin_right.name)
            instance.schema.append([pin_left, pin_right])
    
    def create_component(self) :
        members = {}
        members.update({'schema' :[]})
        self.add_pin_members(members)
        self.add_component_members(members)
        cls = type(str(self.comptype), (Component,), members)
        instance = cls()
        instance.usecase = self.model.usecase
        self.add_connections(instance)
        instance.connect_pins()
        return  instance  