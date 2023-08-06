#encoding:utf-8
#This file contains generic analyses that give some base characteristics of a signal
#
#NB :
#
#as hdf5file cannot be stored as pickable object and open a hdf5 during component execution
#the h5file potential is replaced by its path on the hard disk drive 
from math import log, sqrt, exp
from tables import openFile
from django.conf import settings
from helmholtz.analysis.tools.core.components import BaseComponent,Component
from helmholtz.analysis.tools.core.pins import Parameter,Input,Output,DatabaseObject
from helmholtz.analysis.tools.managers.django_manager import DjangoServerManager
from numpy import array,zeros,ones,convolve,pi,average
from helmholtz.signals.models import Signal

manager = DjangoServerManager()

def get_trace(channel):
    x0 = channel._v_attrs.x0
    dx = channel._v_attrs.dx
    y0 = channel._v_attrs.y0
    dy = channel._v_attrs.dy
    trace_x = channel.read(field='X')*dx + x0
    trace_y = channel.read(field='Y')*dy + y0
    trace = array([trace_x, trace_y])
    return trace

def get_axis(channel,axis):
    a0 = getattr(channel._v_attrs,axis.lower() + '0')
    da = getattr(channel._v_attrs,'d' + axis.lower())
    axis = channel.read(field=axis)*da + a0
    return axis

def get_h5_channel(h5file,signal):
    h5episode = getattr(h5file.root.raw_data,"episode_%s" % (signal.episode))
    h5channel = getattr(h5episode,"channel_%s" % (signal.channel.number))
    return h5channel
    
class PowerMean(BaseComponent):
    """Compute the power mean of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str,usecase="[X, Y]")
    order = Parameter(usecase="order chosen in [-inf:min, -1:harmonic, 0:geometric, 1:arithmetic, 2:quadratic, +inf:max]")
    result = Output() 
    
    def execute(self): 
        warn = """not implemented case, order is in ['-inf', '+inf'] or is an integer"""
        assert isinstance(self.order.potential, int) or (isinstance(self.order.potential, str) and self.order.potential in ['-inf', '+inf']), warn
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        if self.order.potential == '-inf' :
            self.result.potential = axis.min()
        elif self.order.potential == '+inf' :
            self.result.potential = axis.max()
        elif self.order.potential == 0 :
            n = axis.size
            self.result.potential = axis.prod()**(1.0/n)
        else :
            order = self.order.potential
            n = axis.size
            self.result.potential = ((1.0/n)*(axis**order).sum())**(1.0/order) 
        
class Moment(BaseComponent):
    """Compute the nth moment of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str,usecase="[X, Y]")
    order = Parameter(constraint=int,usecase="order of the moment")
    standardized = Parameter(constraint=bool,usecase="tell if the moment is divided by the standard deviation")
    result = Output() 
    
    def execute(self):
        assert self.axis.potential in ['X','Y'], "axis must be 'X' or 'Y'"
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        order = self.order.potential
        moment = (1.0/axis.size)*((axis - axis.mean())**order).sum()
        if self.standardized.potential : 
            moment = moment / axis.std()**self.order.potential
        self.result.potential = moment

class Amplitude(BaseComponent):
    """Compute the amplitude of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str, usecase="[X, Y]")
    result = Output() 
    
    def execute(self):
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        self.result.potential = axis.max() - axis.mean()
    
class PTP(BaseComponent):
    """Compute the peak to peak value of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str, usecase="[X, Y]")
    result = Output() 
    
    def execute(self):
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        self.result.potential = axis.ptp()

class STD(BaseComponent):
    """Compute the peak to peak value of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str, usecase="[X, Y]")
    result = Output() 
    
    def execute(self):
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        self.result.potential = axis.std()

class SNR(BaseComponent):
    """Compute the signal to noise ratio of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str, usecase="[X, Y]")
    result = Output()
    
    def execute(self):
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        self.result.potential = abs(axis.mean() / axis.std()) 

class CV(BaseComponent):
    """Compute the coefficient of variation of a signal contained in a hdf5 file"""
    version = 1
    signal = DatabaseObject(manager,Signal,usecase="signal containing the trace to analyse")
    axis = Parameter(constraint=str, usecase="[X, Y]")
    result = Output()
    
    def execute(self):
        h5file = self.extra_parameters['h5file']
        channel = get_h5_channel(h5file,self.signal.potential)
        axis = get_axis(channel,self.axis.potential)
        self.result.potential = abs(100*(axis.std() / axis.mean()))
        
        