from helmholtz.analysis.tools.factories.common import ObjectFactory
from helmholtz.analysis.models import Analysis as ModelAnalysis
from helmholtz.analysis.tools.analyses import Extern,Analysis

class AnalysisFactory(ObjectFactory) :
    """Automatic Analysis Generation. Take a django object and generate the analysis configuration class."""
    
    def __init__(self, config) :
        """Configure default analysis configuration."""
        self.analysis = ModelAnalysis.objects.get(id=config)
        self.antype = self.analysis.id
        self.snapshot = False
        self.register = False
        self.auto = False
        self.parallel = False
        self.comments = self.analysis.comments
    
    def create_members(self, members) :
        """Create dictionary containing inputs and parameters extracted from database.""" 
        extern = []
        inputs = self.analysis.inputs.all()
        for input in inputs :
            destination = input.pin.name
            if input.existing_potential :
                source_pin = input.existing_potential.pin.name
                source_analysis = ModelAnalysis.objects.get(outputs = input.existing_potential)
                members.update({destination : Extern(source_analysis.id, source_pin)})
            else :
                members.update({destination : input.python_object})
    
    def create_analysis(self, component) :
        members = {}
        self.create_members(members)
        cls = type(str(self.antype), (Analysis,), members)
        instance = cls(component)
        #
        instance.from_db = True
        instance.register = self.register
        instance.auto = self.auto
        instance.parallel = self.parallel
        instance.snapshot = self.snapshot
        instance.component = component
        instance.comments = self.comments
        return  instance