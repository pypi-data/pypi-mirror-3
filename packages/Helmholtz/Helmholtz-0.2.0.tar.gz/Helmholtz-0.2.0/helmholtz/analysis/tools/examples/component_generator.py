#from component import *
from Component.component import *
from Component.db_manager import *
from Component.factory import *

import gnosis.xml.objectify as gxo
#import logging
from NeuroTools.facets import fkbtools
from NeuroTools import parameters
from NeuroTools.stgen import StGen
from NeuroTools.signals import SpikeTrain, SpikeList
import shutil
import os
import atexit
import numpy
import matplotlib
from numpy import sin, cos, exp, pi, sqrt
import sys
sys.path.append('/home/thierry/Benchmarks_Project/svn-trunk/examples')
from myutilities import *
from Benchmarks import plotting
import Benchmarks.analysis
from analysis_test import SpikeGenerator
#from component import authenticate, authentication
#from db_manager import DjangoManager
#from factory import ComponentFactory, AnalysisFactory, RegisteredFactory
#from helmholtz.vision import models

from math import pi
from copy import deepcopy
from NeuroTools.plotting import SimpleMultiplot
from pprint import pprint

parameter_file = "simpleV1.param"
curdir,pyc = os.path.split(os.path.abspath(__file__))
P = parameters.read_parameters(os.path.join(curdir,parameter_file))
#console.setLevel(logging.WARNING)

stimulus_url = "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080804-1034.zip"
scale_factor = 50.0
repetitions = 5
bin_size = 50.0
f_stim = 3.3 # Hz
display = True
max_luminance = 94
background_luminance = 47
MAX_COL = 1

def filter_stimulus_variables(stimulus_variables, all_vars, use_vars):
    filtered_variables = deepcopy(stimulus_variables)
    mask = []
    for var in use_vars:
        mask.append(all_vars.index(var))
    for i,line in enumerate(filtered_variables):
        entries = line.split(',')
        if len(entries) > 1:
            filtered_variables[i] = ",".join(numpy.array(line.split(','))[mask])
    return filtered_variables

if display:
    import pylab
    pylab.rcParams['interactive'] = True
    pylab.rcParams['ytick.labelsize'] = 4
    pylab.rcParams['xtick.labelsize'] = 6
    
    spike_fig = SimpleMultiplot(P['n_cells']+3, min(MAX_COL, repetitions))
    filtered_fig = SimpleMultiplot(P['n_cells']+3, min(MAX_COL, repetitions))
    merged_fig = SimpleMultiplot(P['n_cells']+3, min(MAX_COL, repetitions))

    def plot_spike_hist(fig, spike_list, with_variables=True):
        #spike_hist = spike_list.spike_histogram(bin_size, normalized=False, display=False)
        #time = pylab.arange(spike_hist.shape[1])*bin_size
        time = spike_list.time_axis(bin_size)
        spike_hist = spike_list.spike_histogram(time, normalized=False, display=False)
        y_max = spike_hist.max()
        x_max = time.max()
        for row in spike_hist:
            panel = fig.next_panel()
            panel.plot1(time, row)
            panel.set_xlim(0, x_max)
            panel.set_ylim(0, y_max)
            panel.set_yticks(range(0, y_max, 5))
        if with_variables:
            for i, label, y_max in [(0, 'Contrast', 1.0), (1, 'Orientation (deg)', 135), (2, 'Spatial freq. (cycles/deg)', 20.0)]:
                var_panel = fig.next_panel()
                values = [((v!='null') and eval(v)[i] or None) for v in frame_variables]
                var_panel.plot1(time, values)
                var_panel.set_xlim(0, x_max)
                var_panel.set_ylim(0, y_max)
                var_panel.set_ylabel(label, fontsize=4)
                #var_panel.set_yticks([0,y_max])
if __name__ == '__main__' :    
    #logging.warning('Warning : Launch SpikeGenerator Test 2')
    
    #inputs = {'P' : P, 
    #                'measureable' : 'spikes',
    #                'brain_region_dict' : {'not-specified': {'not-specified': P['n_cells']}},
    #                'figures' : {},
    #                'stimulus_url' : "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080731-1631.zip",
    #                'scale_factor' : 50.0,
    #                'max_luminance' : None,
    #                'background_luminance' : None,
    #                'quiet' : False,
    #                'repetitions' : 10}
    #spikegenerator = SpikeGenerator(inputs) #Create and configure a SpikeGenerator instance
    #spikegenerator.register(auto=True) #Register the instance and force its subcomponents registration
    #spikegenerator.process(parallel=False) #Launch the analysis corresponding to the instance
    #spikegenerator.snapshot("SpikeGenerator Test 2") #Store pickable inputs and outputs of the analysis
    #spikegenerator.db_info() #Query the database to have info concerning the analysis
    #del spikegenerator
    default_manager = DjangoManager()
    authenticate('tbrizzi', 'django2007', default_manager)
    
    logging.warning('Warning : Launch SpikeGenerator Test 3')
    
    class SpikeGeneratorTest3(Analysis) :
        """Test analysis class"""
        P = P
        measureable = 'spikes'
        brain_region_dict = {'not-specified': {'not-specified': P['n_cells']}}
        figures = {}
        stimulus_url = "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080804-1034.zip"
        scale_factor = 50.0
        max_luminance = 94
        background_luminance = 47
        quiet = False
        repetitions = 5    
    
    spikegenerator = SpikeGenerator()
    analysis = SpikeGeneratorTest3(spikegenerator, default_manager)
    analysis.launch(register=True, auto=True, parallel=False, snapshot=True)
    #spikegenerator.db_info()
    
    #==> Old analysis in order to compare results
    
    frame_variables = spikegenerator.orientations.potential
    
    all_vars = ['contrast', 'orientation', 'spatial_freq']
    print "frame_variables[-10:] = ", frame_variables[-10:]
    filtered_variables = filter_stimulus_variables(frame_variables, all_vars, ['orientation', 'spatial_freq'])
    print "filtered_variables[-10:] = ",filtered_variables[-10:]
    preferred = Benchmarks.analysis.find_preferred(spikegenerator.spikelists.potential, filtered_variables)
    ##preferred = Benchmarks.analysis.find_preferred(results, frame_variables, mask=slice(1,3))
    print "Preferred = ", preferred
    
    # Compare measured to actual preferred orientation
    for cell_id, pref in preferred.items():
        print cell_id, spikegenerator.cells_cache.potential[cell_id].theta*180.0/pi, pref
    
    filtered_results = Benchmarks.analysis.filter_by_preferred(spikegenerator.spikelists.potential, filtered_variables)
    ##filtered_results = Benchmarks.analysis.filter_by_preferred(results, frame_variables, mask=slice(1,3))
    
    if display:
        for spikelist in filtered_results[:MAX_COL]:
            plot_spike_hist(filtered_fig, spikelist, with_variables=True)
            filtered_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_filtered.png")
    
    # merge, then f1f0_ratios
    merged_results = Benchmarks.analysis.merge_trials(filtered_results, relative_times=False)
    
    if display:
        plot_spike_hist(merged_fig, merged_results, with_variables=True)
        merged_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_merged.png")
    
    contrast_times = filter_stimulus_variables(frame_variables, all_vars, ['contrast'])
    print "contrast_times[-10:]:", contrast_times[-10:]
    tuning_curves = Benchmarks.analysis.tuning_curves([merged_results], contrast_times, 'mean')
    pprint(tuning_curves)
    
    fitting_result = Benchmarks.analysis.curve_fitting(tuning_curves,
                                                       "Levenberg-Marquardt",
                                                       "hyperbolic ratio",
                                                       normalization="subtract background")
    if display:
        curve_fig = SimpleMultiplot(P['n_cells'], 1, xlabel="Contrast", ylabel="Response", scaling=('log','linear'))
        for id in fitting_result.keys():
            tuning_curve = tuning_curves[id]
            xdata = tuning_curve['mean'].keys()
            xdata.sort()
            ydata = Benchmarks.analysis.subtract_background([tuning_curve['mean'][X] for X in xdata])
            xdata = numpy.array([float(k) for k in xdata])
            
            fit_curve = fitting_result[id]
            xfit = numpy.exp(numpy.arange(numpy.log(0.01), numpy.log(1.0), (numpy.log(0.01)-numpy.log(1.0))/-30.0))
            yfit = fit_curve.function(xfit)
    
            panel = curve_fig.next_panel()
            panel.plot1(xdata, ydata, 'bo', xfit, yfit, 'r-')
        curve_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_curves.png")
    
    pprint(fitting_result)
    
    exponents = Benchmarks.analysis.extract_parameter(fitting_result, 'n')
    
    print exponents
    
    exponent_hist = Benchmarks.analysis.histogram(exponents, 0.3, 0.15, 7.95)
    print exponent_hist
    if display:
        hist_fig = SimpleMultiplot(1, 1, xlabel="Exponent (n)", ylabel="Number of cells")
        hist_fig.next_panel().plot(exponent_hist[1], exponent_hist[0])
        hist_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_histogram.png")
    
    # ==> Do the same stuff with the Component Framework ===
    
    #logging.warning('Warning : Launch F1F0Pipeline Test')
    #
    #xml_component = "/home/thierry/Benchmarks_Project/benchmarks/f1f0_ratio_component.xml" # Component model XML file
    #xml_analysis = "/home/thierry/Benchmarks_Project/benchmarks/f1f0_ratio_analysis.xml" # Component configuration XML file
    #factory = ComponentFactory(xml_component, xml_analysis) # Create a Component from the model and configuration file
    #component, parallel, register, auto, snapshot = factory.create_component() # Return a component instance, process mode, if the instance and its subcomponents could be registered and if the analysis could stored into the database
    #component.process(parallel=parallel) #Launch analysis
    #if register :
    #    component.register(auto=auto) #Register created Component 
    #    if snapshot :
    #        component.snapshot(snapshot) #Store the analysis pickable inputs and results into database
    #component.db_info() #Display component info from database

    logging.warning('Warning : Launch ContrastResponsePipeline Test')
#    gen_obj = models.Component.objects.get(id="SpikeGenerator")
#    print gen_obj.description()
#    spikegenerator.info()
    xml_component = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_component.xml"
    xml_analysis = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_analysis.xml"
    xml_analysis_db = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_analysis_db.xml"
    compfactory = ComponentFactory(xml_component)
    anfactory = AnalysisFactory(xml_analysis)
    #compfactory = RegisteredFactory("ContrastResponsePipeline")
    pipeline = compfactory.create_component()
    
    analysis = anfactory.create_analysis(pipeline)
    analysis.launch(register=True, auto=True, parallel=False, snapshot=True)
    an_obj = models.Analysis.objects.get(id="ContrastResponseTest")
    print an_obj.description()
    #pipeline.db_info()
    #pins = pipeline.retrieve_pins("Contrast Response Test")
    #print pins
    
    # ==> Analysis PostProcessing not really useful, use the old way to debug
    
    frame_variables = spikegenerator.orientations.potential
    filtered_variables = pipeline.filteredvariables.potential
    preferred = pipeline.preferred.potential
    print "frame_variables[-10:] = ", frame_variables[-10:]
    print "filtered_variables[-10:] = ", filtered_variables[-10:]
    print "Preferred = ", preferred
    
    # Compare measured to actual preferred orientation
    for cell_id, pref in preferred.items():
        print cell_id, spikegenerator.cells_cache.potential[cell_id].theta*180.0/pi, pref
    
    if display:
        for spikelist in pipeline.filtered.potential[:MAX_COL]:
            plot_spike_hist(filtered_fig, spikelist, with_variables=True)
            filtered_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_filtered_component.png")
    
    if display:
        plot_spike_hist(merged_fig, pipeline.merged.potential, with_variables=True)
        merged_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_merged_component.png")
    
    contrast_times = pipeline.contrastvariables.potential
    tuning_curves = pipeline.curves.potential
    print "contrast_times[-10:]:", contrast_times[-10:]
    pprint(tuning_curves)
    
    fitting_result = pipeline.fittingresults.potential
    if display:
        curve_fig = SimpleMultiplot(P['n_cells'], 1, xlabel="Contrast", ylabel="Response", scaling=('log','linear'))
        for id in fitting_result.keys():
            tuning_curve = tuning_curves[id]
            xdata = tuning_curve['mean'].keys()
            xdata.sort()
            ydata = Benchmarks.analysis.subtract_background([tuning_curve['mean'][X] for X in xdata])
            xdata = numpy.array([float(k) for k in xdata])
            
            fit_curve = fitting_result[id]
            xfit = numpy.exp(numpy.arange(numpy.log(0.01), numpy.log(1.0), (numpy.log(0.01)-numpy.log(1.0))/-30.0))
            yfit = fit_curve.function(xfit)
    
            panel = curve_fig.next_panel()
            panel.plot1(xdata, ydata, 'bo', xfit, yfit, 'r-')
        curve_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_curves_component.png")
    
    pprint(fitting_result)
    
    exponents = pipeline.histopipeline.extractor.values.potential
    print exponents
    
    exponent_hist = [pipeline.hist.potential, pipeline.bins.potential]
    print exponent_hist
    if display:
        hist_fig = SimpleMultiplot(1, 1, xlabel="Exponent (n)", ylabel="Number of cells")
        hist_fig.next_panel().plot(exponent_hist[1], exponent_hist[0])
        hist_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_contrast_response_histogram_component.png")
    
    print "Done !!!"
