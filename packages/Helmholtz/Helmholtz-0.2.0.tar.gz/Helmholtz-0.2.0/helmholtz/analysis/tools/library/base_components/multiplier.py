from helmholtz.analysis.tools.pins import Pin, Input, Parameter, Output, Debug
from helmholtz.analysis.tools.components import BaseComponent, Component

class Multiplier(BaseComponent) :
    """A component that multiply two integer inputs"""
    def __init__(self) :
        self.parameter1 = Parameter(constraint=int,usecase='parameter1')
        self.input1 = Input(constraint=int,usecase='input1')
        self.parameter2 = Parameter(constraint=int,usecase='parameter2')
        self.input2 = Input(constraint=int,usecase='input2')
        self.output = Output(constraint=int,usecase='returns parameter1*input1 + parameter2*input2')
        super(Multiplier, self).__init__()
    
    def execute(self) :
        self.output.potential = self.parameter1.potential*self.input1.potential + self.parameter2.potential*self.input2.potential

class Multipliers(Component):
    input1 = Input(constraint=int, usecase='input1')
    input2 = Input(constraint=int, usecase='input2')
    input3 = Input(constraint=int, usecase='input3')
    input4 = Input(constraint=int, usecase='input4')
    
    output = Output(constraint=int, usecase='returns input1*input2*input3*input4')
    
    multiplier1 = Multiplier()
    multiplier2 = Multiplier()
    multiplier3 = Multiplier()
    
    schema = [[input1, multiplier1.input1],
              [input2, multiplier1.input2],
              [input3, multiplier2.input1],
              [input4, multiplier2.input2],
              [multiplier1.output, multiplier3.input1],
              [multiplier2.output, multiplier3.input2],
              [multiplier3.output, output]
             ]