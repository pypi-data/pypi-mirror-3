from component import Pin, Input, Parameter, Output, BaseComponent, Component
import sys
sys.path.append('/home/thierry/Benchmarks_Project/svn-trunk/examples')
sys.path.append('/home/thierry/Benchmarks_Project/benchmarks')
from NeuroTools.analysis import TuningCurve
from NeuroTools.signals import SpikeList
from NeuroTools.facets import fkbtools
import numpy
import matplotlib
from matplotlib import mlab
from copy import deepcopy
try:
    import scipy.stats
    have_scipy = True
except ImportError:
    print "Warning: could not import scipy. Certain statistical tests will not be available."
    have_scipy = False
import shelve
from simpleV1 import plot_hist, load_frames, build, GaborCell, figures
from numpy import sin, cos, exp, pi, sqrt
import os
from myutilities import *
from Benchmarks import plotting
import Benchmarks.analysis

#
#data = shelve.open("/home/thierry/Benchmarks_Project/benchmarks/benchmarks_simpleV1.cache", 'r')
#print data

#TODO :peak_widths, subtract_background, merge_trials, f1f0_ratio, extract_parameter, rms_error, chi_square

# === Assistant Classes and Functions ===
MAX_COL = 2

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


def find_preferred(spikelists, category_time_series):
    """
    In the scenario where some variable changes discontinously during the course
    of the recording, returns for each cell id the value of the variable at which
    the most spikes were recorded.
    The variable may take numeric values or string values (categories).
    """
    
    tuning_curves = {}
    for spikelist in spikelists:
        for cell_id, spike_train in spikelist.spiketrains.items():
            tc = spike_train.tuning_curve(category_time_series, normalized=False, method='mean')
            if tuning_curves.has_key(cell_id):
                tuning_curves[cell_id].add(tc)
            else:
                tuning_curves[cell_id] = TuningCurve(tc)
    logging.debug("  tuning_curves = %s" % str(tuning_curves))
    preferred = {}
    for cell_id, tc in tuning_curves.items():
        preferred[cell_id] = tc.max()[0]
    return preferred

def linreg(x,y):
    assert len(x) == len(y), "%s\n%s" % (x,y)
    A = numpy.ones((len(y), 2), dtype=numpy.float)
    A[:,0] = x
    return numpy.linalg.lstsq(A, y)

def tuning_curve_fit_triangle(tuning_curve, tuning_curve_stderr):
    """
    Given an orientation tuning curve, with standard errors for each datapoint,
    take all those points that are more than one stderr above the spontaneous
    level and that are contiguous to the peak of the curve. Fit separate
    straight lines to the upslope and the downslope*, and return a Triangle
    object.

    *the fit is done by linear regression. The stderrs are not used as weights -
    all points are weighted equally. Not clear if this is correct or not, need
    to check the original papers more carefully.

    See Rose and Blakemore (1974) Exp. Brain Res. 20: 1-17
    """
    orientations = tuning_curve.keys()
    orientations.remove("null")
    orientations = numpy.array(orientations, float)
    orientations.sort()

    spontaneous_response = tuning_curve['null']
    logging.info("Spontaneous response level: %g" % spontaneous_response)
    try:
        response = numpy.array([tuning_curve[theta] for theta in orientations], float)
        significant = numpy.array([tuning_curve[theta]-tuning_curve_stderr[theta] for theta in orientations], float)
    except KeyError: # if keys are strings
        response = numpy.array([tuning_curve[str(theta)] for theta in orientations], float)
        significant = numpy.array([tuning_curve[str(theta)]-tuning_curve_stderr[str(theta)] for theta in orientations], float)
    # offset orientations to get peak in the centre of the curve
    orientation_at_peak = orientations[response.argmax()]
    peak_to_centre = 90.0-float(orientation_at_peak)
    orientations = numpy.array(orientations, float) + peak_to_centre
    orientations = numpy.where(orientations>=180,orientations-180,orientations)
    orientations = numpy.where(orientations<0,orientations+180,orientations)

    # fit
    downslope = {'x':[], 'y':[]}; upslope = {'x':[], 'y':[]}
    for direction, slope in zip((-1,1),(upslope, downslope)):
        i = response.argmax()
        n = len(significant)
        while significant[i] > spontaneous_response:
            slope['y'].append(response[i])
            slope['x'].append(orientations[i])
            i += direction
            if i == n:
                i = 0
            elif i == -1:
                i = n-1
        slope['y'].append(response[i])
        slope['x'].append(orientations[i])
        slope['x'] = numpy.array(slope['x'])
        slope['y'] = numpy.array(slope['y'])
    logging.debug("  orientations: %s" % orientations)
    logging.debug("  response: %s" % response)
    logging.debug("  downslope: %s" % downslope)
    logging.debug("  upslope: %s" % upslope)

    if debug_fig: panel = debug_fig.next_panel()
    err_fmt = """%s significant data point%s in either upslope or downslope.
                 Spontaneous level    = %s
                 Response             = %s
                 Significant response = %s"""
    for slope in downslope, upslope:
        if len(slope['x'])>1:
            m, c = tuple(linreg(slope['x'], slope['y'])[0])
            slope['m'] = m; slope['c'] = c
            if debug_fig: 
                xdata = slope['x']-peak_to_centre
                xdata = numpy.where(xdata<0, xdata+180, xdata)
                panel.plot(xdata, m*slope['x'] + c, 'k', linewidth=2)
            logging.info("Fit: %gx + %g" % (m, c))
        elif len(slope['x']) == 1: # vertical line. Set m to inf and c to the x-intersect rather than the y-intersect
            slope['m'] = numpy.inf; slope['c'] = slope['x']
            logging.warning(err_fmt, "Only one", "", spontaneous_response, response, significant)
        else:
            errmsg = err_fmt % ("No", "s", spontaneous_response, response, significant)
            raise Exception(errmsg)
    cd = downslope['c']; cu = upslope['c']
    md = downslope['m']; mu = upslope['m']
    triangle = Triangle(mu,cu,md,cd,peak_to_centre,spontaneous_response)
    return triangle

def residuals(function):
    def _residuals(p, x, y):
        err = y - function(x, p)
        return err
    return _residuals

def fit_levenberg_marquardt(xdata, ydata, curve):
    
    fit_params = scipy.optimize.leastsq(residuals(curve.function), curve.parameters,
                                        args=(xdata, ydata), full_output=True)
    if fit_params[-1] == 1: # success
        curve.parameters = fit_params[0]
        return curve
    else:
        yfit = curve.function(xdata, fit_params[0])
        raise Exception("Fitting failed (%s)\nxdata: %s\nydata: %s\nyfit: %s" % (fit_params[-2], xdata, ydata, yfit))

class Curve(object):
    pass

class HyperbolicRatio(Curve):
    
    def __init__(self, Rmax=1.0, x50=0.5, n=1.5 ):
        self.Rmax = Rmax
        self.x50 = x50
        self.n = n

    def estimate_initial_parameters(self, xdata, ydata):
        self.Rmax = max(ydata)
        self.x50 = numpy.median(xdata)
    
    def _set_params(self, values):
        self.Rmax, self.x50, self.n = values
    
    def _get_params(self):
        return self.Rmax, self.x50, self.n
    parameters = property(fget=_get_params, fset=_set_params)

    def function(self, x, parameters=None):
        if parameters is not None:
            try:
                Rmax, x50, n = parameters
            except ValueError:
                print "parameters =", parameters
                raise
        else:
            Rmax, x50, n = self.parameters
        xn = x**n
        return Rmax*xn/(x50**n + xn)
    
    def __str__(self):
        return "Curve: %g*x**%g/(%g**%g + x**%g)" % (self.Rmax, self.n, self.x50, self.n, self.n)

    def __repr__(self):
        return self.__str__()

class Triangle(Curve):

    def __init__(self, mu, cu, md, cd, peak_to_centre, spontaneous_response):
        self.mu = mu
        self.cu = cu
        self.md = md
        self.cd = cd
        self.peak_to_centre = peak_to_centre
        self.spontaneous_response = spontaneous_response

    def peak_location(self):
        if self.mu < numpy.inf and self.md > -numpy.inf:
            xc = (self.cd - self.cu)/(self.mu - self.md)
        elif self.mu < numpy.inf: # downslope is vertical, cd should be set to the point where it crosses the x-axis
            xc = self.cd
        elif self.md > -numpy.inf: # upslope is vertical
            xc = self.cu
        else: # both vertical
            assert self.cu == self.cd, "Inconsistent triangle with zero width"
            xc = self.cu
        logging.info("Intersection of fit lines is at %g degrees" % (xc-self.peak_to_centre))
        return xc-self.peak_to_centre

    def halfwidth(self):
        """
        Return the half-width at the level halfway between the spontaneous level
        and the intersection of the lines.
        """
        ys = self.spontaneous_response
        if self.mu < numpy.inf and self.md > -numpy.inf:
            mhwhm = ((ys-self.cd)/self.md - (ys-self.cu)/self.mu)/4.0
        elif self.mu < numpy.inf: # downslope is vertical, cd should be set to the point where it crosses the x-axis
            mhwhm = (self.cd - (ys-self.cu)/self.mu)/4.0
        elif self.md > -numpy.inf: # upslope is vertical
            mhwhm = ((ys-self.cd)/self.md - self.cu)/4.0
        else: # both vertical
            mhwhm = 0.0
        logging.info("Mean half-width at half-maximum: %g degrees" % mhwhm)
        return mhwhm

# === Custom BaseComponent designed from benchmarks analysis functions ===

import Benchmarks
import sys
sys.path.append('/home/thierry/Benchmarks_Project/svn-trunk/examples')
from simpleV1 import figures
import pylab

def plot_spike_hist(fig, spike_list, bin_size, frame_variables, with_variables=True):
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

class PlotSpikeHist(BaseComponent) :
    
    def __init__(self) :
        self.figure = Input()
        self.bin_size = Parameter()
        self.spikelists = Input()
        self.frame_variables = Input()
        self.with_variables = Parameter()
        self.output_dir = Parameter()
        super(PlotSpikeHist, self).__init__()
    
    def execute(self) :
        i=0
        for spikelist in self.spikelists.potential :
            if i < MAX_COL:
                plot_spike_hist(self.figure.potential, spikelist, self.bin_size.potential, self.frame_variables.potential, self.with_variables.potential)
                self.figure.potential.save(self.output_dir.potential)
            i += 1

class MergedPlotSpikeHist(PlotSpikeHist) :
    
    def execute(self) :
        plot_spike_hist(self.figure.potential, self.spikelists.potential, self.bin_size.potential, self.frame_variables.potential, self.with_variables.potential)
        self.figure.potential.save(self.output_dir.potential)

class FilteredPlotSpikeHist(PlotSpikeHist) :
    
    def execute(self) :
        for spikelist in self.spikelists.potential[:MAX_COL] :
            plot_spike_hist(self.figure.potential, spikelist, self.bin_size.potential, self.frame_variables.potential, self.with_variables.potential)
            self.figure.potential.save(self.output_dir.potential)

class TuningCurves(BaseComponent) :
    """In the scenario where some variable changes discontinously during the course
    of the recording, a tuning curve can be constructed in which spikes are
    binned according to the value of the variable at the time of the spike.

    `spikelists` is a list containing SpikeList objects, one for each repetition
      of the stimulus.
    `category_time_series` is a numpy array containing the variable value (the
      'category') at evenly spaced intervals between the start and stop times
      of the SpikeList objects (assumed to be the same for all objects).

    Returns a dictionary, indexed by cell id, whose values are dictionaries
    containing the mean tuning curve and stderr of the tuning curve for each cell.
    """
    
    def __init__(self) :
        self.spikelists = Input()
        self.category_time_series = Input()
        self.method = Parameter()
        self.stats = Output()
        super(TuningCurves, self).__init__()
    
    def execute(self) :
        logging.info('-- Compute Tuning Curve --')
        tuning_curves = {}
        if not isinstance(self.spikelists.potential, list):
            spikelists = [self.spikelists.potential]
        else :
            spikelists = self.spikelists.potential
        for spikelist in spikelists:
            for cell_id, spike_train in spikelist.spiketrains.items():
                tc = spike_train.tuning_curve(self.category_time_series.potential, normalized=False, method=self.method.potential)
                if tuning_curves.has_key(cell_id):
                    tuning_curves[cell_id].add(tc)
                else:
                    tuning_curves[cell_id] = TuningCurve(tc)
        logging.debug("  tuning_curves = %s" % str(tuning_curves))
        stats = {}
        for cell_id, tuning_curve_obj in tuning_curves.items():
            mean, stderr = tuning_curve_obj.stats()
            stats[cell_id] = {'mean': mean, 'stderr': stderr}
        self.stats.potential = stats

class DebugTuningCurves(BaseComponent) :
    
    def __init__(self) :
        self.tuning_curves = Input()
        self.figures = Input()
        self.figures_changed = Output()
        super(DebugTuningCurves, self).__init__()
    
    def execute(self) :
        logging.info('--- Debug Tuning Curves ---')
        xdata = self.tuning_curves.potential[0]['mean'].keys()
        xdata.remove("null")
        xdata.sort()
        cdata = [float(k) for k in xdata]
        self.figures_changed.potential = self.figures.potential.copy()
        for cell_id, tuning_curve in self.tuning_curves.potential.items():
            panel = self.figures_changed.potential['orientations'].next_panel()
            ydata = [tuning_curve['mean'][x] for x in xdata]
            yerr  = [tuning_curve['stderr'][x] for x in xdata]
            panel.errorbar(cdata, ydata, yerr)
        self.figures_changed.potential['orientations']._curr_panel = 0 #for the fit_triangles debug but one line not sufficient to create a new component

class FitTriangles(BaseComponent) :
    
    def __init__(self) :
        self.tuning_curves = Input()
        self.widths = Output()
        self.peaks = Output()
        super(FitTriangles, self).__init__()
    
    def execute(self) :
        widths = []
        peaks = []
        for cell_id, tuning_curve in self.tuning_curves.potential.items():
            logging.info("Calculating orientation tuning curve width for cell #%d" % cell_id)
            triangle = Benchmarks.analysis.tuning_curve_fit_triangle(tuning_curve['mean'], tuning_curve['stderr'])
            hwhm = triangle.halfwidth()
            peak = triangle.peak_location()
            logging.info("Half-width at half-maximum for cell #%d: %g degrees" % (cell_id, hwhm))
            widths.append(hwhm)
            peaks.append(peak)
        self.widths.potential = widths
        self.peaks.potential = peaks

class Histogram(BaseComponent) :
    
    def __init__(self) :
        self.values = Input()
        self.binwidth = Parameter()
        self.minimum = Parameter()
        self.maximum = Parameter()
        self.hist = Output()
        self.bins = Output()
        super(Histogram, self).__init__()
    
    def execute(self) :
        logging.info('-- Compute Histogram ---')
        bins = numpy.arange(self.minimum.potential, self.maximum.potential, self.binwidth.potential)
        self.hist.potential, self.bins.potential = numpy.histogram(self.values.potential, bins)
        logging.info("Tuning curve width distribution:")
        logging.info("%s" % self.bins.potential)
        logging.info("%s" % self.hist.potential)

class DebugHistogram(BaseComponent) :
    
    def __init__(self) :
        self.figures = Input()
        self.hist = Input()
        self.bins = Input()
        self.figures_changed = Output()
        super(DebugHistogram, self).__init__()
    
    def execute(self) :
        logging.debug('-- Debug Histogram ---')
        self.figures_changed.potential = self.figures.potential.copy()
        self.figures_changed.potential['width_histogram'] = Benchmarks.plotting.SimpleMultiplot(1, 1, xlabel="Average half-width (deg)", ylabel="Number of cells")
        panel = self.figures_changed.potential['width_histogram'].next_panel()
        plot_hist(panel, self.hist.potential, self.bins.potential, width=2.0)

class PeakAccuracy(BaseComponent) :
    
    def __init__(self) :
        self.figures = Input()
        self.peaks = Input()
        self.cells = Input()
        self.figures_changed = Output()
        super(PeakAccuracy, self).__init__()
    
    def execute(self) :
        real_peaks = [cell.theta*180/pi for cell in self.cells.potential]
        self.figures_changed.potential = self.figures.potential.copy()
        self.figures_changed.potential['peaks'] = Benchmarks.plotting.SimpleMultiplot(1, 1, xlabel="Gabor orientation (deg)", ylabel="Estimated orientation")
        panel = self.figures_changed.potential['peaks'].next_panel()
        panel.plot(real_peaks, self.peaks.potential, 'ro')

class StoreResult(BaseComponent) :
    def __init__(self) :
        self.figures = Input()
        self.output_dir = Parameter()
        self.saved = Output()
        super(StoreResult, self).__init__()
    
    def execute(self) :
        if os.path.exists(self.output_dir.potential) : 
            for label,fig in self.figures.potential.items():
                fig.save(os.path.join(self.output_dir.potential, "simpleV1_%s_component.png" % label))
        else:
            print "Output directory %s does not exist." % self.output_dir.potential
        self.saved.potential = True

class SpikeHistogram(BaseComponent) :
    """ Calculate the spike histogram from a list of spiketime arrays, one per
    repetition. The spike numbers are normalised to give firing rates in Hz.
    Spike times, binwidth and duration should all be in milliseconds.
    Returns a tuple (firing_rates,bins)
    """
    
    def __init__(self) :
        self.allspiketimes = Input(constraint=list)
        self.binwidth = Parameter()
        self.duration = Input()
        self.spike_histogram = Output()
        super(SpikeHistogram, self).__init__()
    
    def execute(self) :
        logging.info('-- Compute Spike Histogram --')
        bins = numpy.arange(0, self.duration.potential, self.binwidth.potential)
        repetitions = len(self.allspiketimes.potential)
        hist = numpy.zeros(len(bins))
        for spiketimes in self.allspiketimes.potential :
            hist += nstats.histc(spiketimes,bins)*1000.0/self.binwidth.potential
        hist /= repetitions
        self.spike_histogram.potential = (hist,bins)

class MeanFiringRate(BaseComponent) :
    """ Returns mean firing rate in spikes/s.
    Duration should be in ms.
    """
    
    def __init__(self) :
        self.allspiketimes = Input(contraint=list)
        self.duration = Input()
        self.mean_firing_rate = Output()
        super(MeanFiringRate, self).__init__()
    
    def execute(self) :
        logging.info('-- Compute Mean Firing Rate --')
        repetitions = len(self.allspiketimes.potential)
        nspikes = 0
        ncells = 0
        for spikelists in self.allspiketimes.potential : # spikelists is a list of spiketrains, one per cell
            ncells += len(spikelists)
            for spikelist in spikelists:
                nspikes += len(spikelist)
        logging.debug("Mean firing rate = %d/%d/%d/%g = %g" % (nspikes, ncells, repetitions, self.duration.potential/1000.0, nspikes/repetitions/(self.duration.potential/1000.0)))
        self.mean_firing_rate.potential = (nspikes/ncells/repetitions/(self.duration.potential/1000.0),)

class FilterStimulusVariables(BaseComponent) :
    
    def __init__(self) :
        self.stimulus_variables = Input()
        self.all_vars = Parameter()
        self.use_vars = Parameter()
        self.filtered_variables = Output()
        super(FilterStimulusVariables, self).__init__()
    
    def execute(self) :
        self.filtered_variables.potential = deepcopy(self.stimulus_variables.potential)
        mask = []
        for var in self.use_vars.potential :
            mask.append(self.all_vars.potential.index(var))
        for i,line in enumerate(self.filtered_variables.potential):
            entries = line.split(',')
            if len(entries) > 1:
                self.filtered_variables.potential[i] = ",".join(numpy.array(line.split(','))[mask])

class FindPreferred(BaseComponent) :
    """ In the scenario where some variable changes discontinously during the course
    of the recording, returns for each cell id the value of the variable at which
    the most spikes were recorded.
    The variable may take numeric values or string values (categories).
    """
    
    def __init__(self) :
        self.spikelists = Input()
        self.category_time_series = Input()
        self.preferred = Output()
        super(FindPreferred, self).__init__()
    
    def execute(self) :
        logging.info('-- Find Preferred --')
        tuning_curves = {}
        for spikelist in self.spikelists.potential :
            for cell_id, spike_train in spikelist.spiketrains.items():
                tc = spike_train.tuning_curve(self.category_time_series.potential, normalized=False, method='mean')
                if tuning_curves.has_key(cell_id):
                    tuning_curves[cell_id].add(tc)
                else:
                    tuning_curves[cell_id] = TuningCurve(tc)
        logging.debug("  tuning_curves = %s" % str(tuning_curves))
        preferred = {}
        for cell_id, tc in tuning_curves.items():
            preferred[cell_id] = tc.max()[0]
        self.preferred.potential = preferred

class Compare(BaseComponent) :
    
    def __init__(self) :
        self.preferred = Input()
        self.cells = Input()
        super(Compare, self).__init__()
    
    def execute(self) :
        for cell_id, pref in self.preferred.potential.items():
            print cell_id, self.cells.potential[cell_id].theta*180.0/pi, pref

class DisplayRatios(BaseComponent) :
    
    def __init__(self) :
        self.f1f0ratios = Input()
        super(DisplayRatios, self).__init__()
    
    def execute(self) :
        print self.f1f0ratios.potential

def subtract_background(x):
    return x-x[0]

class CurveFitting(BaseComponent) :
    
    def __init__(self) :
        self.tuning_curves = Input()
        self.method = Parameter()
        self.function_name = Parameter()
        self.normalization = Parameter()
        self.curves = Output()
        super(CurveFitting, self).__init__()
    
    def execute(self) :
        logging.info('-- Compute Curve Fitting --')
        if self.normalization.potential:
            norm_func = eval(self.normalization.potential.replace(' ','_'))
        else:
            norm_func = lambda x: x
        curves = {}
        if self.method.potential == "linear regression" and self.function_name.potential == "triangle":
            for cell_id, tuning_curve in self.tuning_curves.potential.items():
                logging.info("Calculating orientation tuning curve width for cell #%d" % cell_id)
                triangle = tuning_curve_fit_triangle(tuning_curve['mean'], tuning_curve['stderr'])
                curves[cell_id] = triangle
        elif self.method.potential == "Levenberg-Marquardt" and self.function_name.potential == "hyperbolic_ratio":
            for cell_id, tuning_curve in self.tuning_curves.potential.items():
                logging.info("Fitting tuning curve with %s function using %s method for cell #%d" % (self.function_name.potential, self.method.potential, cell_id))
                curve = HyperbolicRatio()
                tuning_curve['mean'].pop('null', None)
                xdata = tuning_curve['mean'].keys()
                xdata.sort()
                ydata = numpy.array([tuning_curve['mean'][X] for X in xdata], float)
                xdata = numpy.array([float(k) for k in xdata])
                ydata = norm_func(ydata)
                curve.estimate_initial_parameters(xdata, ydata)
                curve = fit_levenberg_marquardt(xdata, ydata, curve)
                curves[cell_id] = curve
        else:
            raise Exception("Fitting method and/or curve type not yet implemented.")
        self.curves.potential = curves

class FilterByPreferred(BaseComponent) :
    """ Find preferred for each cell and then filter the spike trains to
    leave only spikes that occur while the variable has that value.
    """
    
    def __init__(self) :
        self.spikelists = Input()
        self.category_time_series = Input()
        self.filtered_spikelists = Output()
        super(FilterByPreferred, self).__init__()
    
    def execute(self) :
        logging.info("Filtering %d spikelists with a category_time_series that begins with %s and ends with %s" % (len(self.spikelists.potential), self.category_time_series.potential[:10], self.category_time_series.potential[-10:]))  
        spikelists = self.spikelists.potential  
        category_time_series = numpy.array(self.category_time_series.potential)
        preferred_values = find_preferred(spikelists, category_time_series)
        logging.debug("  Preferred values are: %s" % preferred_values)
        
        # Check that t_start and t_stop is the same for all spikelists
        t_start = spikelists[0].t_start
        t_stop = spikelists[0].t_stop
        for spikelist in spikelists:
            assert spikelist.t_start == t_start and spikelist.t_stop == t_stop
        interval = (t_stop-t_start)/len(category_time_series)
        logging.debug("  t_start = %g, t_stop = %g, interval = %g" % (t_start, t_stop, interval))
        
        filtered_spikelists = []
        for spikelist in spikelists:
            filtered_spikelist = SpikeList([], [], spikelist.dt)
            for cell_id, spiketrain in spikelist.spiketrains.items():
                preferred_value = preferred_values[cell_id]
                mask = (category_time_series==preferred_value)
                # Calculate times at which the category has the preferred value
                time_points = numpy.arange(t_start, t_stop, interval)
                start_times = time_points[mask]
                time_points = numpy.roll(time_points, -1)
                time_points[-1] = time_points[-2] + interval
                stop_times = time_points[mask]
                assert stop_times[-1] > start_times[-1]
                # Filter the spiketrain and add to the new spikelist
                filtered_spiketrain = spiketrain.subSpikeTrain(start_times, stop_times)
                filtered_spiketrain.t_start = t_start
                filtered_spiketrain.t_stop = t_stop
                filtered_spikelist.append(cell_id, filtered_spiketrain)
            filtered_spikelists.append(filtered_spikelist)
        self.filtered_spikelists.potential = filtered_spikelists

class PeakWidths(BaseComponent) :
    """ Given a dictionary containing Curve objects (usually with cell ids as
    dictionary keys, although we just throw these away, return a list containing
    the widths of the Curves.
    """
    
    def __init__(self) :
        self.curve_dict = Input()
        self.widths = Output()
        super(PeakWidths, self).__init__()
    
    def execute(self) :
        widths = []
        for curve in self.curve_dict.potential.values():
            widths.append(curve.halfwidth())
        self.widths.potential = widths

class MergeTrials(BaseComponent) :
    """ Merge all the spikelists into a single spikelist (i.e. for all spike trains
    that have the same id in each spikelist, merge the spike trains into a
    single spike train.
    """
    
    def __init__(self) :
        self.spikelists = Input()
        self.relative_times = Parameter()
        self.merged_spikelist = Output()
        super(MergeTrials, self).__init__()
    
    def execute(self):
        merged_spikelist = deepcopy(self.spikelists.potential[0]) # don't want to modify the original data, so deepcopy
        if len(self.spikelists.potential) > 1:
            for spikelist in self.spikelists.potential[1:]:
                merged_spikelist.merge(spikelist, relative_times=self.relative_times.potential) # overlay all trials by making all spiketimes relative to t_start (i.e. setting t_start to 0)
        self.merged_spikelist.potential = merged_spikelist

class F1F0Ratio(BaseComponent) : 
    """
    Calculates the F1/F0 ratios for stimulus frequency `f_stim`.
    """
    
    def __init__(self) :
        self.spikelist = Input()
        self.bin_width = Parameter()
        self.f_stim = Parameter()
        self.ratios = Output()
        super(F1F0Ratio, self).__init__()
    
    def execute(self) :
        self.ratios.potential = self.spikelist.potential.f1f0_ratios(self.bin_width.potential, self.f_stim.potential).values()

class ExtractParameters(BaseComponent) :
    
    def __init__(self) :
        self.curve_dict = Input()
        self.parameter = Parameter()
        self.values = Output()
        super(ExtractParameters, self).__init__()
    
    def execute(self) :
        values = []
        for curve in self.curve_dict.potential.values():
            values.append(getattr(curve, self.parameter.potential))
        self.values.potential = values

class RMSError(BaseComponent) :
    """ The experimental data should be passed as xdata1,ydata1, the model results
    as xdata2, ydata2.
    The value of ydata2 is calculated by interpolation at each value of xdata1,
    and the rms difference between ydata1 and the interpolated ydata2 is
    returned.
    """

    def __init__(self) :
        self.xdata1 = Input()
        self.ydata1 = Input()
        self.xdata2 = Input()
        self.ydata2 = Input()
        self.panel = Input()
        self.err = Output()
    
    def execute(self) :
        ydata2i = mlab.stineman_interp(self.xdata1.potential, self.xdata2.potential, self.ydata2.potential)
        self.panel.potential.plot(self.xdata1.potential, ydata2i)
        assert len(self.ydata1.potential)==len(ydata2i)
        self.err.potential = numpy.sqrt(numpy.sum(numpy.square(self.ydata1.potential-ydata2i))/len(self.ydata1.potential))

class ChiSquare(BaseComponent) :
    """
    The experimental data should be passed as xdata1,ydata1, the model results
    as xdata2, ydata2.
    xdata1 and xdata2 should be identical.
    """
    
    def __init__(self) :
        self.exp_data = Input()
        self.model_xdata = Input()
        self.model_ydata = Input()
        self.result = Output()
        super(ChiSquare, self).__init__()

    def execute(self):
        """
        The experimental data should be passed as xdata1,ydata1, the model results
        as xdata2, ydata2.
        xdata1 and xdata2 should be identical.
        """
        def rebin(ydata1, ydata2):
            new_ydata1 = []; new_ydata2 = []; y2_sum = 0
            for y1,y2 in zip(ydata1, ydata2):
                y2_sum += y2
                if y1 != 0:
                    new_ydata1.append(y1)
                    new_ydata2.append(y2_sum)
                    y2_sum = 0
            assert sum(new_ydata1) == sum(ydata1)
            assert sum(new_ydata2) == sum(ydata2)
            return numpy.array(new_ydata1), numpy.array(new_ydata2)
        
        logging.info("Running chi-square test")
        xdata1 = self.exp_data.potential[0]
        ydata1 = self.exp_data.potential[1]
        xdata2 = self.model_xdata.potential
        ydata2 = self.model_ydata.potential
        assert len(xdata1) == len(xdata2) == len(ydata1) == len(ydata2)
        assert all(numpy.array(xdata1)-numpy.array(xdata2)<1e-12), str(numpy.array(xdata1)-numpy.array(xdata2))
        # if experimental data (ydata1) contains zeros, need to re-bin both datasets
        # To be implemented
        if 0 in ydata1:
            logging.warning("Experimental data contains zero-frequency values. Re-binning.")
            logging.debug("  Original data: %s\n                 %s" % (ydata1, ydata2))
            ydata1, ydata2 = rebin(ydata1, ydata2)
            logging.debug("  Re-binned data: %s\n                  %s" % (ydata1, ydata2))
        if sum(ydata1) != sum(ydata2): # normalize model distribution to have same number of events as experimental data
            logging.warning("Normalising model distribution (%d events) to have same number of events as experimental data (%d events)" % (sum(ydata1),sum(ydata2)))
            ydata2 = numpy.array(ydata2)/float(sum(ydata2))*sum(ydata1)
        if have_scipy:
            self.result.potential = scipy.stats.chisquare(f_obs=ydata2, f_exp=ydata1)[0]
        else:
            logging.warning("Warning: scipy not available. Returning a fake value.")
            self.result.potential = 99999
