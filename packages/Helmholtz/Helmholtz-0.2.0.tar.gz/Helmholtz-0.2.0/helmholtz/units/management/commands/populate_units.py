#encoding:utf-8
#command useful to store all S.I. units and their dependencies
#data are available at the following address : http://www.bipm.org
from helmholtz.core.populate import PopulateCommand
from helmholtz.units.models import BaseUnit, DerivedUnit

#base units
base_units = [
    {'symbol':'m', 'name':'metre', 'physical_meaning':'length', 'math_symbol':'l'}, #
    {'symbol':'kg', 'name':'kilogram', 'physical_meaning':'mass', 'math_symbol':'m'}, #
    {'symbol':'s', 'name':'second', 'physical_meaning':'time', 'math_symbol':'t'}, #
    {'symbol':'A', 'name':'ampere', 'physical_meaning':'electric current', 'math_symbol':'i'}, #
    {'symbol':'K', 'name':'kelvin', 'physical_meaning':'thermodynamic temperature', 'math_symbol':'T'}, #
    {'symbol':'mol', 'name':'mole', 'physical_meaning':'amount of substance', 'math_symbol':'n'}, #
    {'symbol':'cd', 'name':'candela', 'physical_meaning':'luminous intensity', 'math_symbol':'I<sub>V</sub>'},
]

geometric_units = [
    {'symbol':'m&sup2;', 'name':'square metre', 'physical_meaning':'surface', 'math_symbol':'A'}, #
    {'symbol':'m&sup3;', 'name':'cubic metre', 'physical_meaning':'volume', 'math_symbol':'V'}, #
    {'symbol':'1/m', 'name':'unit per metre', 'physical_meaning':'wavelength,vergence', 'math_symbol':'&sigma;'}, #
    {'symbol':'sr', 'name':'steradian', 'physical_meaning':'solid angle', 'math_symbol':'&theta;'}#
]

mass_units = [
    {'symbol':'kg/m', 'name':'kilogram per metre', 'physical_meaning':'linear density', 'math_symbol':'&mu;'}, #
    {'symbol':'kg/m&sup2;', 'name':'kilogram per square metre', 'physical_meaning':'surface density', 'math_symbol':'&rho;<sub>A</sub>'}, #
    {'symbol':'kg/m&sup3;', 'name':'kilogram per cubic metre', 'physical_meaning':'volume density,concentration', 'math_symbol':'&rho;'}, #
    {'symbol':'m&sup3;/kg', 'name':'cubic metre per kilogram', 'physical_meaning':'mass volume', 'math_symbol':'v'}, #
]

mechanic_units = [
    {'symbol':'m/s', 'name':'metre per second', 'physical_meaning':'velocity', 'math_symbol':'v'}, #
    {'symbol':'rad/s', 'name':'radian per second', 'physical_meaning':'angular velocity', 'math_symbol':'n'}, #
    {'symbol':'m/s&sup2;', 'name':'metre per square second', 'physical_meaning':'acceleration', 'math_symbol':'a'}, #
    {'symbol':'rad/s&sup2;', 'name':'radian per square second', 'physical_meaning':'angular acceleration', 'math_symbol':"&alpha;"}, #
    {'symbol':'N', 'name':'newton', 'physical_meaning':'force', 'math_symbol':'F'}, #
    {'symbol':'N/m&sup2;', 'name':'newton per square metre', 'physical_meaning':'pressure,stress', 'math_symbol':'p'}, #
    {'symbol':'Pa.s', 'name':'pascal second', 'physical_meaning':'dynamic viscosity', 'math_symbol':'&mu;'}, #
    {'symbol':'N.m', 'name':'metre newton', 'physical_meaning':'moment of force', 'math_symbol':"&tau;"}, #
    {'symbol':'N/m', 'name':'newton per metre', 'physical_meaning':'surface tension', "math_symbol":"&gamma;"}, # 
    {'symbol':'rad', 'name':'radian', 'physical_meaning':'angle', 'math_symbol':'&theta;'}, #
]

photometry_units = [
    {'symbol':'cd/m&sup2;', 'name':'candela per square metre', 'physical_meaning':'luminance', 'math_symbol':'L<sub>V</sub>'}, #
    {'symbol':'lm', 'name':'lumen', 'physical_meaning':'luminous flux', 'math_symbol':'F'}, #
    {'symbol':'lx', 'name':'lux', 'physical_meaning':'illuminance', 'math_symbol':'E<sub>V</sub>'}, #
    {'symbol':'W/sr', 'name':'watt per steradian', 'physical_meaning':'energetic luminance'}, #
    {'symbol':'W/(m&sup2;.sr)', 'name':'watt per square metre steradian', 'physical_meaning':'energetic intensity'}, #
]

thermodynamic_units = [
    {'symbol':'J', 'name':'joule', 'physical_meaning':'energy,work,quantity of heat'}, #
    {'symbol':'W', 'name':'watt', 'physical_meaning':'power,radiant flux'}, #
    {'symbol':'W/m&sup2;', 'name':'watt per square metre', 'physical_meaning':'heat flux density,irradiance'}, #
    {'symbol':'J/K', 'name':'joule per kelvin', 'physical_meaning':'heat capacity,entropy'}, #
    {'symbol':'J/kg.K', 'name':'joule per kilogram kelvin', 'physical_meaning':'specific heat capacity,specific entropy'}, #
    {'symbol':'J/kg', 'name':'joule per kilogram', 'physical_meaning':'specific energy'}, #
    {'symbol':'W/m.K', 'name':'watt per meter kelvin', 'physical_meaning':'thermal conductivity'}, #
    {'symbol':'J/m&sup3;', 'name':'joule per cubic meter', 'physical_meaning':'energy density'}, #
    {'symbol':'J/mol', 'name':'joule per mole', 'physical_meaning':'molar energy'}, #
    {'symbol':'J/mol.K', 'name':'joule per mole kelvin', 'physical_meaning':'molar entropy,molar heat capacity'}, #
    {'symbol':'kat', 'name':'katal', 'physical_meaning':'katalitic activity'}, #
    {'symbol':'kat/m&sup3;', 'name':'katal per cubic metre', 'physical_meaning':'katalitic activity concentration'}, #
    {'symbol':'e.V', 'name':'electronvolt', 'physical_meaning':'energy,work,quantity of heat'}, #
    {'symbol':'Wh', 'name':'watthour', 'physical_meaning':'energy,work,quantity of heat'}, #
]

radiation_units = [
    {'symbol':'Bq', 'name':'becquerel', 'physical_meaning':'activity (ionizing radiations)'}, #
    {'symbol':'Gy', 'name':'gray', 'physical_meaning':'absorbed dose'}, #
    {'symbol':'Gy/s', 'name':'gray per second', 'physical_meaning':'absorbed dose rate'}, #
    {'symbol':'C/kg', 'name':'coulomb per kilogram', 'physical_meaning':'exposure (ionizing radiations)'}, #
    {'symbol':'Sv', 'name':'sievert', 'physical_meaning':'equivalent dose (ambiant,directional,individual)'}, #
]

electromagnetism_units = [
    {'symbol':'Hz', 'name':'herz', 'physical_meaning':'frequency'}, #
    {'symbol':'C', 'name':'coulomb', 'physical_meaning':'electric charge,quantity of electricity', 'math_symbol':'q'}, #
    {'symbol':'V', 'name':'volt', 'physical_meaning':'electric potential', 'math_symbol':'U'}, #
    {'symbol':'F', 'name':'farad', 'physical_meaning':'capacitance', 'math_symbol':'C'}, #
    {'symbol':'&Omega;', 'name':'ohm', 'physical_meaning':'electric resistance', 'math_symbol':'R'}, #
    {'symbol':'S', 'name':'siemens', 'physical_meaning':'conductance', 'math_symbol':'G'}, #
    {'symbol':'S/m', 'name':'siemens per metre', 'physical_meaning':'linear conductivity', 'math_symbol':'&sigma;'}, #
    {'symbol':'S/m&sup2;', 'name':'siemens per square metre', 'physical_meaning':'surface conductivity', 'math_symbol':'&sigma;<sub>A</sub>'}, #
    {'symbol':'S/m&sup3;', 'name':'siemens per square metre', 'physical_meaning':'volume conductivity', 'math_symbol':'&sigma;<sub>V</sub>'}, #
    {'symbol':'Wb', 'name':'weber', 'physical_meaning':'magnetic flux'}, #
    {'symbol':'T', 'name':'tesla', 'physical_meaning':'magnetic flux density,magnetic induction', 'math_symbol':'&Phi;'}, #
    {'symbol':'H', 'name':'henry', 'physical_meaning':'inductance', 'math_symbol':'L'}, # 
    {'symbol':'V/m', 'name':'volt per metre', 'physical_meaning':'electric field strength', 'math_symbol':'E'}, #
    {'symbol':'C/m&sup3;', 'name':'coulomb per cubic metre', 'physical_meaning':'electric charge density'}, #
    {'symbol':'C/m&sup2;', 'name':'coulomb per square metre', 'physical_meaning':'electric displacement,electric flux density'}, #
    {'symbol':'F/m', 'name':'farad per metre', 'physical_meaning':'electrical permittivity', 'math_symbol':'&epsilon;'}, #
    {'symbol':'H/m', 'name':'henry per metre', 'physical_meaning':'magnetical permeability', 'math_symbol':'&mu;'}, #
]

other_units = [
    #discrete image and volume
    {'symbol':'px', 'name':'pixel', 'physical_meaning':'picture element'},
    {'symbol':'vx', 'name':'voxel', 'physical_meaning':'volume element'},
    #statistics
    {'symbol':'%', 'name':'percent', 'physical_meaning':'percentage'},
]

#BaseUnit objects
base_units.extend(geometric_units)
base_units.extend(mass_units)
base_units.extend(mechanic_units)
base_units.extend(photometry_units)
base_units.extend(thermodynamic_units)
base_units.extend(radiation_units)
base_units.extend(electromagnetism_units)
base_units.extend(other_units)

#DerivedUnit objects
derived_units = [
    {'symbol':'l', 'name':'litre', 'base_unit':{'name':'cubic metre'}, 'multiplier':'1e-3'}, #
    {'symbol':'a', 'name':'are', 'base_unit':{'name':'square metre'}, 'multiplier':'1e2'}, #
    {'symbol':'ha', 'name':'hectare', 'base_unit':{'name':'square metre'}, 'multiplier':'1e4'}, #
    {'symbol':'&deg;', 'name':'degree', 'base_unit':{'name':'radian'}, 'multiplier':'pi/180'}, #
    {'symbol':'t', 'name':'ton', 'base_unit':{'name':'kilogram'}, 'multiplier':'1e3'}, #
    {'symbol':'min', 'name':'minute', 'base_unit':{'name':'second'}, 'multiplier':'60'}, #
    {'symbol':'h', 'name':'hour', 'base_unit':{'name':'second'}, 'multiplier':'3600'}, #
    {'symbol':'d', 'name':'day', 'base_unit':{'name':'second'}, 'multiplier':'86400'}, #
    {'symbol':'&deg;C', 'name':'degree celsius', 'base_unit':{'name':'kelvin'}, 'offset':'273.15'}, #
    {'symbol':'&deg;F', 'name':'degree fahrenheit', 'base_unit':{'name':'kelvin'}, 'multiplier':'5.0/9', 'offset':'459.67*5/9'}, #
    {'symbol':'Pa', 'name':'pascal', 'base_unit':{'name':'newton per square metre'}, 'multiplier':'1'}, #
    {'symbol':'bar', 'name':'bar', 'base_unit':{'name':'newton per square metre'}, 'multiplier':'1e6'}, #
    #distance
    {'symbol':'km', 'name':'kilometre', 'base_unit':{'name':'metre'}, 'multiplier':'1e3'},
    {'symbol':'hm', 'name':'hectometre', 'base_unit':{'name':'metre'}, 'multiplier':'1e2'},
    {'symbol':'dam', 'name':'decametre', 'base_unit':{'name':'metre'}, 'multiplier':'10'},
    {'symbol':'dm', 'name':'decimetre', 'base_unit':{'name':'metre'}, 'multiplier':'1e-1'},
    {'symbol':'cm', 'name':'centimetre', 'base_unit':{'name':'metre'}, 'multiplier':'1e-2'},
    {'symbol':'mm', 'name':'millimetre', 'base_unit':{'name':'metre'}, 'multiplier':'1e-3'},
    {'symbol':'&mu;m', 'name':'micrometre', 'base_unit':{'name':'metre'}, 'multiplier':'1e-6'},
    {'symbol':'nm', 'name':'nanometre', 'base_unit':{'name':'metre'}, 'multiplier':'1e-9'},
    #resistance
    {'symbol':'G&Omega;', 'name':'gigohm', 'base_unit':{'name':'ohm'}, 'multiplier':'1e9'},
    {'symbol':'M&Omega;', 'name':'megohm', 'base_unit':{'name':'ohm'}, 'multiplier':'1e6'},
    {'symbol':'k&Omega;', 'name':'kilohm', 'base_unit':{'name':'ohm'}, 'multiplier':'1e3'},
    #voltage
    {'symbol':'GV', 'name':'gigavolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e9'},
    {'symbol':'MV', 'name':'megavolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e6'},
    {'symbol':'kV', 'name':'kilovolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e3'},
    {'symbol':'mV', 'name':'millivolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e-3'},
    {'symbol':'&mu;V', 'name':'microvolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e-6'},
    {'symbol':'nV', 'name':'nanovolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e-9'},
    {'symbol':'pV', 'name':'picovolt', 'base_unit':{'name':'volt'}, 'multiplier':'1e-12'},
    #current
    {'symbol':'nA', 'name':'nanoampere', 'base_unit':{'name':'ampere'}, 'multiplier':'1e-9'},
    {'symbol':'pA', 'name':'picoampere', 'base_unit':{'name':'ampere'}, 'multiplier':'1e-12'},
    #time
    {'symbol':'ms', 'name':'millisecond', 'base_unit':{'name':'second'}, 'multiplier':'1e-3'},
    {'symbol':'&mu;s', 'name':'microsecond', 'base_unit':{'name':'second'}, 'multiplier':'1e-6'},
    {'symbol':'ns', 'name':'nanosecond', 'base_unit':{'name':'second'}, 'multiplier':'1e-9'},
    {'symbol':'ps', 'name':'picosecond', 'base_unit':{'name':'second'}, 'multiplier':'1e-12'},
]

class Command(PopulateCommand):
    help = "populate units"
    priority = 0
    data = [
        {'class':BaseUnit, 'objects':base_units},
        {'class':DerivedUnit, 'objects':derived_units}    
    ]

if __name__ == '__main__' :
    command = Command()
    command.handle_noargs()
