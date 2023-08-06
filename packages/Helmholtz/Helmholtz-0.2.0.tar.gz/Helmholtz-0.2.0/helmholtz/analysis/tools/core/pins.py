class Pin(object) :
    """Describe an Input or Output of a Component :
    
    - name : name (alias) of the pin
    - type : type constraint
    - usecase : description of the pin,
    - potential : an object of type Connection,
    - component : the component that use this pin,
    - connected_to : list of other pins connected to the current pin
    
    """ 
    def __init__(self,constraint,usecase) :
        super(Pin, self).__init__()
        self.constraint = constraint
        self.usecase = usecase
        self.name = None
        self.potential = None
        self.component = None
        self.connected_to = []
    
    def _type(self):
        return self.__class__.__name__
    type = property(_type)

#These classes discriminate the different component pins
class Input(Pin) : 
    """Input of a Component."""
    def __init__(self,constraint=None, usecase=None) :
        super(Input,self).__init__(constraint,usecase)

class DatabaseObject(Input):
    """Input that extract data from the database."""
    def __init__(self,manager,entity,usecase=None) :
        self.manager = manager
        super(DatabaseObject,self).__init__(entity,usecase)

class DatabaseValue(Input):
    """Input that extract data from a field of the database."""
    def __init__(self,manager,entity,field,usecase=None) :
        assert hasattr(entity,field)
        self.manager = manager
        self.object = None
        self.field = field
        super(DatabaseObject,self).__init__(entity,usecase)

class Output(Pin) : 
    """Output of a component."""
    def __init__(self,constraint=None,usecase=None) :
        super(Output,self).__init__(constraint,usecase)

class FileOutput(Output) : 
    """Output of a component stored in a file."""
    def __init__(self,root=None,usecase=None) :
        self.root = None
        super(Output,self).__init__(str,usecase)

class Parameter(Input) : 
    """Input considered as a parameter of a component."""
    def __init__(self,constraint=None,usecase=None) :
        super(Parameter,self).__init__(constraint,usecase)
        
class DatabaseObjectParameter(Input):
    """Input that extract data from the database."""
    def __init__(self,manager,entity,usecase=None) :
        self.manager = manager
        super(DatabaseObject,self).__init__(entity,usecase)

class DatabaseValueParameter(Input):
    """Input that extract data from a field of the database."""
    def __init__(self,manager,entity,field,usecase=None) :
        assert hasattr(entity,field)
        self.manager = manager
        self.object = None
        self.field = field
        super(DatabaseObject,self).__init__(entity,usecase)