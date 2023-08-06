import sys
sys.path.append('/home/thierry/Benchmarks_Project/svn-trunk/examples')
import simpleV1
import logging
import Benchmarks.analysis
from math import pi
from copy import deepcopy
from NeuroTools.plotting import SimpleMultiplot
import analysis_test
from analysis_test import SpikeGenerator
from component import *
from custom_component import  FindPreferred, FilterByPreferred, MergeTrials, F1F0Ratio, Compare, DisplayRatios, PlotSpikeHist, MergedPlotSpikeHist, FilteredPlotSpikeHist
P = simpleV1.P
stimulus_url = "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080731-1631.zip"
scale_factor = 50.0
repetitions = 10
bin_size = 50.0
f_stim = 1.0 # Hz
display = True
max_luminance = None
background_luminance = None
MAX_COL = 2

class AnalysisPipeline(Component) :
    
    spikelists = Input()
    orientations = Input()
    bin_size = Input()
    f_stim = Input()
    relative_times = Input()
    preferred = Output()
    filtered = Output()
    merged = Output()
    f1f0ratios = Output()
    
    findpreferred = FindPreferred()
    filterbypreferred = FilterByPreferred()
    mergetrials = MergeTrials()
    f1f0ratio = F1F0Ratio()
    
    schema = [[spikelists, findpreferred.spikelists],
                      [spikelists, filterbypreferred.spikelists],
                      [orientations, findpreferred.category_time_series],
                      [orientations, filterbypreferred.category_time_series],
                      [relative_times, mergetrials.relative_times],
                      [bin_size, f1f0ratio.bin_width],
                      [f_stim, f1f0ratio.f_stim],
                      [filterbypreferred.filtered_spikelists, mergetrials.spikelists],
                      [mergetrials.merged_spikelist, f1f0ratio.spikelist],
                      [preferred, findpreferred.preferred],
                      [filtered, filterbypreferred.filtered_spikelists],
                      [merged, mergetrials.merged_spikelist],
                      [f1f0ratios, f1f0ratio.ratios]
                    ]

""" XML Specification : 

- separated in 2 files, one for the component specification, another for the configuration
- the configuration file is the file that launch the component generation and computation
- configuration file :
    - choose the component to use
    - define values associated to each input
    - if the input require a python object, execute the component that generate this object or query the database to retrieve persisted data
"""

class AnalysisPostProcessing(Component) :
    
    cells = Input()
    fig_spikes = Input()  
    fig_spikes_path = Input()  
    fig_filtered = Input()  
    fig_filtered_path = Input()  
    fig_merged = Input()  
    fig_merged_path = Input()  
    spikes = Input()
    preferred = Input()
    filtered = Input()
    merged = Input() 
    f1f0ratios = Input()
    bin_size = Input()
    orientations = Input()
    with_variables_spikes = Input()
    with_variables_other = Input()
    
    spikes_plotspikehist = PlotSpikeHist()
    filtered_plotspikehist = FilteredPlotSpikeHist()
    merged_plotspikehist = MergedPlotSpikeHist()
    compare = Compare()
    display_ratios = DisplayRatios()
    
    schema = [[cells, compare.cells],
                      [preferred, compare.preferred],
                      [f1f0ratios, display_ratios.f1f0ratios],
                      [fig_spikes, spikes_plotspikehist.figure],
                      [fig_spikes_path, spikes_plotspikehist.output_dir],
                      [bin_size, spikes_plotspikehist.bin_size],
                      [with_variables_spikes, spikes_plotspikehist.with_variables],
                      [spikes, spikes_plotspikehist.spikelists],
                      [orientations, spikes_plotspikehist.frame_variables],
                      [fig_filtered, filtered_plotspikehist.figure],
                      [fig_filtered_path, filtered_plotspikehist.output_dir],
                      [bin_size, filtered_plotspikehist.bin_size],
                      [with_variables_other, filtered_plotspikehist.with_variables],
                      [filtered, filtered_plotspikehist.spikelists],
                      [orientations, filtered_plotspikehist.frame_variables],
                      [fig_merged, merged_plotspikehist.figure],
                      [fig_merged_path, merged_plotspikehist.output_dir],
                      [bin_size, merged_plotspikehist.bin_size],
                      [with_variables_other, merged_plotspikehist.with_variables],
                      [merged, merged_plotspikehist.spikelists],
                      [orientations, merged_plotspikehist.frame_variables],
                    ]

if __name__ == '__main__' : 
    
    if display:
        import pylab
        pylab.rcParams['interactive'] = True
        pylab.rcParams['ytick.labelsize'] = 4
        pylab.rcParams['xtick.labelsize'] = 6
        
        spike_fig = SimpleMultiplot(P['n_cells']+2, min(MAX_COL, repetitions))
        filtered_fig = SimpleMultiplot(P['n_cells'], min(MAX_COL, repetitions))
        merged_fig = SimpleMultiplot(P['n_cells'], min(MAX_COL, repetitions))

    def plot_spike_hist(fig, spike_list, with_variables=True):
        spike_hist = spike_list.spike_histogram(bin_size, normalized=False, display=False)
        time = pylab.arange(spike_hist.shape[1])*bin_size
        y_max = spike_hist.max()
        x_max = time.max()
        for row in spike_hist:
            panel = fig.next_panel()
            panel.plot1(time, row)
            panel.set_xlim(0, x_max)
            panel.set_ylim(0, y_max)
            panel.set_yticks(range(0, y_max, 5))
        if with_variables:
            for i, label, y_max in [(0, 'Orientation (deg)', 135), (1, 'Spatial freq. (cycles/deg)', 20.0)]:
                var_panel = fig.next_panel()
                values = [((v!='null') and eval(v)[i] or None) for v in frame_variables]
                var_panel.plot1(time, values)
                var_panel.set_xlim(0, x_max)
                var_panel.set_ylim(0, y_max)
                var_panel.set_ylabel(label, fontsize=4)
                #var_panel.set_yticks([0,y_max])

    #==> Replace the SimpleV1 spike generation with the SpikeGenerator

    logging.warning('Warning : Launch SpikeGenerator.')
    inputs = {'P' : P, 
                   'measureable' : 'spikes',
                    'brain_region_dict' : {'not-specified': {'not-specified': P['n_cells']}},
                    'figures' : {},
                    'stimulus_url' : "file:///home/thierry/Benchmarks_Project/benchmarks/multiple_gratings_20080731-1631.zip",
                    'scale_factor' : 50.0,
                    'max_luminance' : None,
                    'background_luminance' : None,
                    'quiet' : False,
                    'repetitions' : 10}
    spikegenerator = SpikeGenerator(inputs)
    spikegenerator.process(parallel=False)
    
    #==> Old analysis in order to compare results
    
    frame_variables = spikegenerator.orientations.potential
    print "frame_variables[-10:] = ", frame_variables[-10:]
    
    i = 0
    for spike_list in spikegenerator.spikelists.potential :
        if display and i < MAX_COL:
            plot_spike_hist(spike_fig, spike_list)
            spike_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_f1f0_spikes.png")
        i += 1
    
    results = spikegenerator.spikelists.potential    
    preferred = Benchmarks.analysis.find_preferred(results, frame_variables)
    
    # Compare measured to actual preferred orientation
    cells = [k for k in spikegenerator.cells_cache.potential]
    for cell_id, pref in preferred.items():
        print cell_id, cells[cell_id].theta*180.0/pi, pref
    
    filtered_results = Benchmarks.analysis.filter_by_preferred(results, frame_variables)
    
    if display:
        i = 0
        for spikelist in filtered_results[:MAX_COL]:
            plot_spike_hist(filtered_fig, spikelist, with_variables=False)
            filtered_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_f1f0_filtered.png")
            i += 1
    
    # merge, then f1f0_ratios
    merged_results = Benchmarks.analysis.merge_trials(filtered_results)
    
    if display:
        plot_spike_hist(merged_fig, merged_results, with_variables=False)
        merged_fig.save("/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_f1f0_merged.png")
    
    f1f0_ratios = Benchmarks.analysis.f1f0_ratio(merged_results, bin_size, f_stim)
    
    print f1f0_ratios
    
    # ==> Do the same stuff with the Component Framework ===
    
    inputs = {'spikelists' : spikegenerator.spikelists.potential,
                    'orientations' :spikegenerator.orientations.potential,
                    'bin_size' : 50.0,
                    'f_stim' : 1.0,
                    'relative_times' : True}
    pipeline = AnalysisPipeline(inputs)
    pipeline.process(parallel=False)
    
    inputs = {'bin_size' : 50,
                    'cells' : spikegenerator.cells_cache.potential,
                    'orientations' : spikegenerator.orientations.potential, 
                    'spikes' : spikegenerator.spikelists.potential,
                    'preferred' : pipeline.preferred.potential,
                    'filtered' : pipeline.filtered.potential,
                    'merged' : pipeline.merged.potential,
                    'f1f0ratios' : pipeline.f1f0ratios.potential,
                    'with_variables_spikes' : True,
                    'with_variables_other' : False,
                    'fig_spikes' : SimpleMultiplot(P['n_cells']+2, min(MAX_COL, repetitions)),
                    'fig_spikes_path' : "/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_f1f0_spikes_2.png",
                    'fig_filtered' : SimpleMultiplot(P['n_cells'], min(MAX_COL, repetitions)),
                    'fig_filtered_path' : "/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_f1f0_filtered_2.png",
                    'fig_merged': SimpleMultiplot(P['n_cells'], min(MAX_COL, repetitions)),
                    'fig_merged_path': "/home/thierry/Benchmarks_Project/benchmarks/Results/simpleV1/test_f1f0_merged_2.png"}
    
    postprocess = AnalysisPostProcessing(inputs)
    postprocess.process(parallel=False)
    
    input = {}
    analysis = Analysis(input)
    analysis.process(parallel=False)
