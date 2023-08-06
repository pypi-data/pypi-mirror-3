import sys
sys.path.append('/home/thierry/Benchmarks_Project/svn-trunk/examples')
import simpleV1
import logging
import Benchmarks.analysis
from math import pi
from copy import deepcopy
from NeuroTools.plotting import SimpleMultiplot
import numpy
from pprint import pprint
import analysis_test
from analysis_test import SpikeGenerator
from test_f1f0 import AnalysisPipeline as F1F0AnalysisPipeline
from component import *
from custom_component import  TuningCurves, CurveFitting, ExtractParameters, Histogram, FilterStimulusVariables

P = simpleV1.P
stimulus_url = "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080804-1034.zip"
scale_factor = 50.0
repetitions = 5
bin_size = 50.0
f_stim = 3.3 # Hz
display = True
max_luminance = None
background_luminance = None
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

class HistoPipeline(Component) :
    
    merged = Input()
    contrasttimes = Input()
    tuningmethod = Input()
    fittingmethod = Input()
    function = Input()
    normalization = Input()
    parameter = Input()
    binwidth = Input()
    minimum = Input()
    maximum = Input()
    hist = Output()
    bins = Output()
    curves = Output()
    fittingresults = Output()
    
    tuningcurves = TuningCurves()
    curvefitting = CurveFitting()
    extractor = ExtractParameters()
    histogram = Histogram()
    
    schema = [#Inputs
                      [merged, tuningcurves.spikelists],
                      [tuningmethod, tuningcurves.method],
                      [contrasttimes, tuningcurves.category_time_series],
                      [function, curvefitting.function_name],
                      [normalization, curvefitting.normalization],
                      [fittingmethod, curvefitting.method],
                      [parameter, extractor.parameter],
                      [binwidth, histogram.binwidth],
                      [minimum, histogram.minimum],
                      [maximum, histogram.maximum],
                      #nterconnections
                      [tuningcurves.stats, curvefitting.tuning_curves],
                      [curvefitting.curves, extractor.curve_dict],
                      [extractor.values, histogram.values],
                      #Outputs
                      [hist, histogram.hist],
                      [bins, histogram.bins],
                      [curves, tuningcurves.stats],
                      [fittingresults, curvefitting.curves]
                      ]

class AnalysisPipeline(Component) :
    
    #Inputs
    spikelists = Input()
    orientations = Input()
    all_vars = Input()
    use_vars = Input()
    use_vars_contrast = Input()
    relative_times = Input()
    bin_size = Input()
    f_stim = Input()
    tuningmethod = Input()
    fittingmethod = Input()
    fittingfunction = Input()
    normalization = Input()
    parameter = Input()
    binwidth = Input()
    minimum = Input()
    maximum = Input()
    #Outputs
    preferred = Output()
    filtered = Output()
    merged = Output()
    ratios = Output()
    hist = Output()
    bins = Output()
    filteredvariables = Output()
    contrastvariables = Output()
    curves = Output()
    fittingresults = Output()
    #Components
    filtervariables = FilterStimulusVariables()
    f1f0pipeline = F1F0AnalysisPipeline()
    contrasttimes = FilterStimulusVariables()
    histopipeline = HistoPipeline()
    #Connections
    schema = [#Inputs
                     [spikelists, f1f0pipeline.spikelists],
                     [orientations, filtervariables.stimulus_variables],
                     [all_vars, filtervariables.all_vars],
                     [use_vars, filtervariables.use_vars],
                     [orientations, contrasttimes.stimulus_variables],
                     [all_vars, contrasttimes.all_vars],
                     [use_vars_contrast, contrasttimes.use_vars],
                     [relative_times, f1f0pipeline.relative_times],
                     [bin_size, f1f0pipeline.bin_size],
                     [f_stim, f1f0pipeline.f_stim],
                     [binwidth, histopipeline.binwidth],
                     [minimum, histopipeline.minimum],
                     [maximum, histopipeline.maximum],
                     [tuningmethod, histopipeline.tuningmethod],
                     [fittingmethod, histopipeline.fittingmethod],
                     [fittingfunction, histopipeline.function],
                     [normalization, histopipeline.normalization],
                     [parameter, histopipeline.parameter],
                     #Interconnections
                     [filtervariables.filtered_variables, f1f0pipeline.orientations],
                     [contrasttimes.filtered_variables, histopipeline.contrasttimes],
                     [f1f0pipeline.merged, histopipeline.merged],
                     #Outputs
                     [ratios, f1f0pipeline.f1f0ratios],
                     [preferred, f1f0pipeline.preferred],
                     [filtered, f1f0pipeline.filtered],
                     [merged, f1f0pipeline.merged],
                     [hist, histopipeline.hist],
                     [bins, histopipeline.bins],
                     [filteredvariables, filtervariables.filtered_variables],
                     [contrastvariables, contrasttimes.filtered_variables],
                     [curves, histopipeline.curves],
                     [fittingresults, histopipeline.fittingresults]
                    ]

if __name__ == "__main__" :

    #==> Replace the SimpleV1 spike generation with the SpikeGenerator
    
    inputs = {'P' : P, 
                   'measureable' : 'spikes',
                    'brain_region_dict' : {'not-specified': {'not-specified': P['n_cells']}},
                    'figures' : {},
                    'stimulus_url' : "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080804-1034.zip",
                    'scale_factor' : 50.0,
                    'max_luminance' : None,
                    'background_luminance' : None,
                    'quiet' : False,
                    'repetitions' : 5}
    spikegenerator = SpikeGenerator(inputs)
    spikegenerator.process(parallel=False)
    
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
    
    inputs = {'spikelists' : spikegenerator.spikelists.potential,
                    'orientations' :spikegenerator.orientations.potential,
                    'bin_size' : 50.0,
                    'f_stim' : 3.3,
                    'relative_times' : False,
                    'all_vars' : ['contrast', 'orientation', 'spatial_freq'],
                    'use_vars' : ['orientation', 'spatial_freq'],
                    'use_vars_contrast' : ['contrast'],
                    'tuningmethod' : 'mean',
                    'fittingmethod' : "Levenberg-Marquardt",
                    'fittingfunction' : "hyperbolic ratio",
                    'normalization' : "subtract background",
                    'parameter' : 'n',
                    'binwidth' : 0.3,
                    'minimum' :  0.15,
                    'maximum' : 7.95}
    pipeline = AnalysisPipeline(inputs)
    pipeline.process(parallel=False)
    
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
