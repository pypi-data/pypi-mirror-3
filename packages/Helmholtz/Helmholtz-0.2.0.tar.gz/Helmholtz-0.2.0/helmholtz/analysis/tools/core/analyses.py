#encoding:utf-8

class Extern(object) :
    """Analysis field that reflects data coming from a database."""
    def __init__(self, analysis, pin) :
        self.analysis = analysis
        self.pin = pin

class Analysis(object) :
    
    def __init__(self) :
        self.inputs = {}
        self.extern = {}
        self.list_of_inputs = {}
        self.snapshot = self.__class__.__name__
        self.comments = self.__class__.__doc__
        #self.from_xml = False
        #self.from_db = False   