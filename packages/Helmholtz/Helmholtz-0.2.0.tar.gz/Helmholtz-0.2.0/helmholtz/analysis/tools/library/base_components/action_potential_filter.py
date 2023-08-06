from helmholtz.analysis.tools.components import BaseComponent
from helmholtz.analysis.tools.pins import Parameter, Output

class SubLiminarActivity(BaseComponent):
    
    h5file = Parameter(constraint=str, usecase="path of the hdf5 file on the server")
    episodes = Parameter(constraint=list, usecase="list of selected episodes")
    channel = Parameter(constraint=int, usecase="selected channel")
    threshold = Parameter(constraint=int, usecase="threshold useful to discriminate if a signal variation could be considered as an action potential")
    up_interval = Parameter(constraint=float, usecase="")
    down_interval = Parameter(constraint=float, usecase="")
    activity = Output(usecase="sub liminar activity")
    
    def execute(self):
        pass
        #recherche des variations brutales ascendantes entre deux points consecutifs au delà de 1mV
        #on a un si dans les 2ms qui suivent on trouve une variation descendante du même ordre