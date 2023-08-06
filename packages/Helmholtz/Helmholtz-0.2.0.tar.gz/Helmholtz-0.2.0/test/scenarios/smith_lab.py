# encoding: utf-8
"""
This script populates a test database for the Helmholtz system.
"""

"""
We start off with the Smith Laboratory, which does patch electrode recordings in
hippocampal slices.

First, let's set up some administrative information:
"""

from helmholtz.people.models import ScientificStructure, Contact, Address, Researcher, Position, PositionType
import datetime

print "Running Smith Laboratory scenario"

univ = ScientificStructure(name="University of Somewhere")
univ.create_diminutive()
univ.save()
lab = ScientificStructure(name="Smith Lab", parent=univ)
lab.create_diminutive()
lab.save()

#secretary = Contact(label="secretary",
#                    address=Address(street_address_1="32 SomeStreet",
#                                    town="Someplace",
#                                    postal_code="99999",
#                                    country="Nowhereland"),
#                    e_mail="admin@somelab.example.com",
#                    phone_number="+33 1 69 82 41 96",
#                    website="http://somelab.example.com/"
#                   )
#secretary.address.save()
#secretary.save()
#lab.contacts.add(secretary)
#lab.save()

professor = PositionType("Professor")
postdoc = PositionType("Postdoc")
student = PositionType("Grad student")
for pt in professor, postdoc, student:
    pt.save()

prof_smith = Researcher(first_name="Sue", last_name="Smith")
prof_smith.save()
prof_smith.position_set.create(structure=lab, position_type=professor, start=datetime.date(1984, 9, 1))
#prof_smith.contacts.create(e_mail="smith@somelab.example.com")
prof_smith.save()

tony = Researcher(first_name="Tony", last_name="Wu")
tony.save()
tony.position_set.create(structure=lab, position_type=postdoc, start=datetime.date(2012, 5, 23))
tony.save()

alice = Researcher(first_name="Alice", last_name="Dubois")
alice.save()
alice.position_set.create(structure=lab, position_type=student, start=datetime.date(2010, 10, 1))
alice.save()

"""
The Smith Lab has two patch setups. Both setups use Axopatch amplifiers and
Olympus microscopes.
"""
from helmholtz.equipment.models import EquipmentType, GenericEquipment, Setup, Device, SubSystem
from helmholtz.people.models import Supplier
olympus = Supplier(name="Olympus")
olympus.save()
microscope = EquipmentType("microscope")
microscope.save()
bx51wi = GenericEquipment(type=microscope, manufacturer=olympus,
                          model="BX51WI")
bx51wi.save()
amplifier = EquipmentType(name="amplifier")
amplifier.save()
mds = Supplier(name="MDS Analytical Technologies")
mds.save()
axopatch = GenericEquipment(type=amplifier, manufacturer=mds,
                            model="Axopatch 200B-10400")
axopatch.save()

my_amp = Device(equipment=axopatch, serial_or_id="ABC123")
my_amp.save()
my_microscope = Device(equipment=bx51wi)
my_microscope.save()

amps = SubSystem(label="amplifiers")
amps.save()
amps.devices.add(my_amp)
amps.save()
vis = SubSystem(label="visualisation")
vis.save()
vis.devices.add(my_microscope)
vis.save()
setup = Setup(place=lab, room="C253")
setup.save()
setup.subsystems.add(amps, vis)
setup.save()
    
"""
The Smith Lab uses Wistar rats.
"""
from helmholtz.species.models import Strain, Species
from helmholtz.preparations.models import Animal

brown_rat = Species(english_name="brown rat", scientific_name="Rattus norvegicus", id=180363)
brown_rat.save()
wistar = Strain(name="Wistar",
                species=brown_rat)
wistar.save()
                
ratsrus = Supplier(name="Rats R Us")
ratsrus.save()

rats = [
    Animal(strain=wistar, identifier="#00%d" % i, sex='M',
           birth=datetime.date(2011, 6, 17),
           supplier=ratsrus,
          ) for i in range(10)
       ]
for rat in rats:
    rat.save()

"""
Recordings are made in the hippocampus, areas CA1 and CA3. We use the Swanson
nomenclature, obtained from BrainInfo http://braininfo.rprc.washington.edu/Nnont.aspx
"""

from helmholtz.neuralstructures.models import BrainRegion
from helmholtz.location.models import Position
import xlrd

book = xlrd.open_workbook('NN2007MouseandRatNomenclatures.xls')
swanson = book.sheet_by_name('Swanson')

for i in range(1, swanson.nrows):
    name, abbrev = swanson.cell(i,0).value, swanson.cell(i,1).value
    br = BrainRegion(species=wistar.species, english_name=name,
                     abbreviation=abbrev)
    br.save()

CA1 = BrainRegion.objects.get(abbreviation="CA1")
CA3 = BrainRegion.objects.get(abbreviation="CA3")

CA1_recording_position = Position(brain_region=CA1, lt_axis="L") #, intra=True)
CA1_recording_position.save()
CA3_recording_position = Position(brain_region=CA3, lt_axis="L") #, intra=True)
CA3_recording_position.save()

"""
Now let's make up the slice solutions
"""

from helmholtz.units.fields import PhysicalQuantity as Q
from helmholtz.chemistry.models import Substance,Product,Solution,QuantityOfSubstance

NaCl = Substance("NaCl")
KCl = Substance("KCl")
KH2PO4 = Substance(u"KH₂PO₄")
NaH2PO4 = Substance(u"NaH₂PO₄")
MgSO4 = Substance(u"MgSO₄")
CaCl2 = Substance(u"CaCl₂")
NaHCO3 = Substance(u"NaHCO₃")
glucose = Substance("glucose")
K_gluconate = Substance("K-gluconate")
MgCl2 = Substance(u"MgCl₂")
EGTA = Substance("EGTA")
MgATP = Substance("MgATP")
HEPES = Substance("HEPES")
    
walmart = Supplier(name="WalMart")
walmart.save()

cutting_solution = Solution(label="ACSF 1")
cutting_solution.save()

components = [
    (NaCl,      Q(134.0, "mM")),
    (KCl,       Q(5.0, "mM")),
    (KH2PO4,    Q(1.25, "mM")),
    (MgSO4,     Q(2.0, "mM")),
    (CaCl2,     Q(1.0, "mM")),
    (NaHCO3,    Q(16.0, "mM")),
    (glucose,   Q(10.0, "mM")),
]

for substance_type, conc in components:
    substance_type.save()
    product = Product(name=substance_type.name,
                      substance=substance_type,
                      supplier=walmart)
    product.save()
    cutting_solution.quantityofsubstance_set.add(
        QuantityOfSubstance(chemical_product=product, concentration=conc))

bath_solution = cutting_solution

pipette_solution = Solution(label="patch pipette solution")
pipette_solution.save()

components = [
    (K_gluconate, Q(110, "mM")),
    (KCl,         Q(20, "mM")),         
    (MgCl2,       Q(1, "mM")),
    (EGTA,        Q(5, "mM")),
    (MgATP,       Q(5, "mM")),
    (HEPES,       Q(10, "mM")),
]
for substance_type, conc in components:
    substance_type.save()
    product, created = Product.objects.get_or_create( # we use get_or_create because KCl was previously created
                            name=substance_type.name,
                            substance=substance_type,
                            supplier=walmart)
    pipette_solution.quantityofsubstance_set.add(
        QuantityOfSubstance(chemical_product=product, concentration=conc))


		
"""
Now let's specify the slice preparations
"""

from helmholtz.preparations.models import Preparation,InVitroSlice

preparations = [InVitroSlice(thickness=Q(400, u"µm"),
                             cutting_solution=cutting_solution,
                             bath_solution=bath_solution,
                             protocol="Description of protocol goes here",
                             animal=rat)
                for rat in rats]
for p in preparations:
    p.save()


    
"""
Now let's specify the recording configuration
"""

from helmholtz.equipment.models import Material

borosilicate = Material(name="borosilicate glass", supplier=Supplier(name="Dagan Corporation"))
borosilicate.save()
borosilicate.supplier.save()

electrode_info = dict(material=borosilicate,
                      internal_diameter=Q(0.75, "mm"),
                      external_diameter=Q(1.65, "mm"))
electrode_config = dict(seal_resistance=Q(1.5, u"GΩ"),
                        contact_configuration="WC", # whole cell
                        solution=pipette_solution)

"""
Now let's create the experiments.
"""

import datetime
import random
from helmholtz.experiment.models import Experiment
from helmholtz.recording.models import RecordingBlock, RecordingConfiguration
from helmholtz.annotation.models import Descriptor
from helmholtz.measurements.models import FloatMeasurement
from helmholtz.electrophysiology.models import PatchElectrode, PatchElectrodeConfiguration
from helmholtz.units.models import Unit
from helmholtz.drug_applications.models import Perfusion,Injection
from helmholtz.equipment.models import Device

grams = Unit.objects.create(name="gram")

experiments = []
for month,preparation in enumerate(preparations):
    date = datetime.date(2012, month+1, 27)    
    WEIGHT = preparation.add_field("weight", grams)
    weight = FloatMeasurement(parameter=WEIGHT, value=212.0, unit=grams,
                              timestamp=datetime.datetime(2011, 12, 1, 9, 23))
    weight.save()
    preparation.observations.add(weight)
    preparation.save()
    
    preparation.animal.sacrifice = date
    preparation.animal.save()
    expt = Experiment(label=date.strftime("%Y%m%d"),
                      setup=setup,
                      preparation=preparation)
    expt.save()
    researchers = [r for r in prof_smith, tony, alice if r.position_set.all()[0].start < date]
    expt.researchers.add(*researchers)
    expt.save()
    experiments.append(expt)

    """
    drug injection and perfusion
    """	
    anaesthesia  =  Solution(label="Anaesthesia solution")
    anaesthesia.save()
    
    drugsP = Perfusion(experiment=expt, 
                       solution=anaesthesia,
                       start = datetime.datetime(date.year, date.month, date.day, 8, 30, 0),
                       end = datetime.datetime(date.year, date.month, date.day, 10, 00, 0),
                       rate = Q(2.5, 'mL/h'))
    drugsP.save()

    muscle_relaxant = Solution(label="Muscle Relaxant solution")
    muscle_relaxant.save()

    drugsI = Injection(experiment=expt, 
                       solution=muscle_relaxant,
                       volume=Q(38, 'mL'),
                       time=datetime.datetime(date.year, date.month, date.day, 11, 10, 0))
    drugsI.save()
    
#    """
#	now let's specify the animal preparation
#    """
#    APreparation = AreaCentralis(	preparation=preparation,
#									left_x=Q(1,u"mm"),
#									left_y=Q(3,u"mm"),
#									right_x=Q(4,u"mm"),
#									right_y=Q(2,u"mm"))
#    APreparation.save()
#
#    Epreparation = [EyeCorrection(	preparation=preparation,
#									left=Q(2,u"delta"),
#									right=Q(4,u"delta"))]
#    for e in Epreparation:
#        e.save()


    n_blocks = random.randint(1,6)
    start = datetime.datetime(date.year, date.month, date.day, 9, 11, 0)
    for i in range(n_blocks):
        end = start + datetime.timedelta(0, 60*random.randint(30, 360))
        block = RecordingBlock(experiment=expt, label='ABCDEFG'[i],
                               start=start, end=end)
        block.save()
        start = end
        
        CA1_electrode = PatchElectrode(**electrode_info)
        CA3_electrode = PatchElectrode(**electrode_info)
        CA1_electrode_conf = PatchElectrodeConfiguration(**electrode_config)
        CA3_electrode_conf = PatchElectrodeConfiguration(**electrode_config)
        for electrode in CA1_electrode, CA3_electrode:
            electrode.save()
        for conf in CA1_electrode_conf, CA3_electrode_conf:
            conf.save()
        dev_CA1 = Device(equipment=CA1_electrode)
        dev_CA1.save()
        dev_CA3 = Device(equipment=CA3_electrode)
        dev_CA3.save()
        rc_CA1 = RecordingConfiguration(block=block, position=CA1_recording_position, device=dev_CA1, configuration=CA1_electrode_conf)
        rc_CA3 = RecordingConfiguration(block=block, position=CA3_recording_position, device=dev_CA3, configuration=CA3_electrode_conf)
            #tip = RecordingPoint(point_number=0, electrode=electrode)
            #tip.save()
        rc_CA1.save()
        rc_CA3.save()

"""
The slices are stimulated using stimulating electrodes in the dentate gyrus, and
recordings are made in current clamp. All the signals for a given protocol
(multiple presentations of the same stimulus) are stored in a single file.
"""

from helmholtz.recording.models import ProtocolRecording
from helmholtz.waveforms.models import PulseSequence
from helmholtz.electricalstimulation.models import ElectricalStimulus
from helmholtz.electrophysiology.models import ElectricalRecordingMode, ElectricalChannel
from helmholtz.signals.models import ChannelType, Signal
from helmholtz.storage.models import File, FileServer, MimeType

pulse_sequence = PulseSequence(frequency=Q(1, "Hz"), amplitude=Q(2.3, "nA"),
                               duration=Q(100, "ms"))
pulse_sequence.save()
stimulus = ElectricalStimulus(waveform=pulse_sequence)
stimulus.save()

current_clamp = ElectricalRecordingMode(name="current clamp")
current_clamp.save()

Vm = ChannelType(name="Membrane potential")
Vm.save()

#hdf5 = MimeType(name="application/x-hdf", extension="h5")
#hdf5.save()
#filesystem = FileServer(protocol="file", ip_address="", label="laptop")
#filesystem.save()
#print filesystem

#for block in RecordingBlock.objects.all():
#    electrodes = {}; recording_points = {}
#    for area in "CA1", "CA3":
#            electrodes[area] = block.configuration_set.get(electrodeconfiguration__position__brain_region__english_name__contains=area).get_subclass()
#            recording_points[area] = electrodes[area].recordingpoint_set.get(point_number=0)
#    n_recordings = random.randint(3,8)
#    for i in range(n_recordings):
#        rec = ProtocolRecording(block=block, stimulus=stimulus)
#        rec.save()
#        
#        file = File(name="%s_%s_%-2d_Vm" % (block.experiment.label, block.label, i),
#                    mimetype=hdf5, filesystem=filesystem, original=True)
#        file.save()
#        
#        recording_modes = {}
#        for area in "CA1", "CA3":
#            recording_modes[area] = ElectricalRecordingMode(mode=current_clamp,
#                                                            electrode=electrodes[area],
#                                                            recording=rec)
#            recording_modes[area].save()
#                        
#            channel = ElectricalChannel(channel_number=0, x_unit='ms', y_unit='mV',
#                                        channel_type=Vm,
#                                        recording_point=recording_points[area],
#                                        protocol=rec)
#            channel.save()
#            
#            n_trials = 5
#            for trial_num in range(n_trials):
#                s = Signal(episode=trial_num, channel=channel, file=file)
#                s.save()
                
