# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:59:45 2016

@author: zhiyiwu
"""


import numpy as np
from sklearn import mixture
# http://scikit-learn.org/stable/
# Machine learning package
import scipy as sp

from dcpyps import dcio

class Cluster():
    def __init__(self, trace = None, dt = None, t_start = 0, open_level = None, baseline = None):
        '''
        '''
        self.trace = trace
        self.dt = dt
        self.t_start = t_start
        self.open_level = open_level
        self.baseline = baseline

    def Popen(self):
        integrated_charge = np.sum(self.trace)
        total_charge = self.open_level * len(self.trace)
        Popen = integrated_charge / total_charge
        return Popen

    def get_t_start(self):
        return self.t_start

    def get_t_end(self):
        return self.t_start + self.dt * len(self.trace)

    def display_trace(self):
        if self.baseline:
            return np.hstack([self.baseline[0], self.trace, self.baseline[1]])
        else:
            return self.trace


    def __str__(self):
        return 'Start time: {start}, End time: {end}'.format(start = self.get_t_start(), end = self.get_t_end())

class Segment(object):
    def __init__(self, trace = None, dt = None, t_start = 0,
                 filter_rising_t = None):
        '''
        '''
        self.trace = np.copy(trace)
        self.dt = dt
        self.t_start = t_start

        self.baseline = None
        self.is_baseline_adjusted = False
        self.open_level = None
        self.adjusted_open_level = None
        self.filter_rising_t = filter_rising_t

    def find_cluster(self):
        '''
        Find the cluster within the start time (s) and the end time (s).
        '''
        
        try:
            self.adjusted_open_level = self.open_level - self.baseline
        except TypeError: # check if self.open_level is None
            self.amplitude_analysis()
            self.adjusted_open_level = self.open_level - self.baseline

        if not self.is_baseline_adjusted: 
            self.trace -= self.baseline
            self.is_baseline_adjusted = True
        idx_start, idx_stop = self.detect_start_stop(self.trace, self.adjusted_open_level)
        adjusted_t_start = self.t_start + self.dt * idx_start
        tenth_length = int((idx_stop-idx_start)/10)
        if (idx_start-tenth_length) > 0:
            baseline_start = idx_start-tenth_length
        else:
            baseline_start = 0

        if (idx_stop+tenth_length) < len(adjusted_trace):
            baseline_stop = idx_stop+tenth_length
        else:
            baseline_stop = len(adjusted_trace)

        cluster = Cluster(trace = adjusted_trace[idx_start: idx_stop],
                          dt = self.dt, t_start = adjusted_t_start,
                          open_level = adjusted_open_level,
                          baseline = [adjusted_trace[baseline_start:idx_start], adjusted_trace[idx_stop:baseline_stop]])
        return cluster

    def amplitude_analysis(self, method = 'filter'):
        '''
        Automatical snalysis the baseline and conductance.
        self.baseline and self.open_level are set in this function but can also
        be set by other function or manually.
        '''
        if method == 'GMM':
            g = mixture.GMM(n_components=2)
            temp = np.expand_dims(self.trace, axis=1)
            e=g.fit(temp)
            self.baseline, self.open_level = min(e.means_), max(e.means_)
        elif method == 'filter':
            # take the 99% quantile as the maximum amplitude
            estimate_open_level = np.percentile(self.trace, 99)
            # take the 1% quantile as the minimum amplitude
            estimate_baseline = np.percentile(self.trace, 1)

            half_amplitude = (estimate_open_level + estimate_baseline) / 2
            above_half_amplitude = np.where(self.trace > half_amplitude)[0]
            length_filter = int(np.ceil(self.filter_rising_t/self.dt))
            sample_index = 10e-3 / self.dt
            baseline_before = max(0, above_half_amplitude[0]-length_filter - sample_index)
            baseline_1 = self.trace[int(baseline_before): int(above_half_amplitude[0]-length_filter)]
            baseline_after = min(len(self.trace), above_half_amplitude[-1]+length_filter+sample_index)
            baseline_2 = self.trace[int(above_half_amplitude[-1]+length_filter):int(baseline_after)]

            p_value = sp.stats.ttest_ind(baseline_1, baseline_2)[1]



            split_index = np.split(above_half_amplitude,
                                   np.where(np.diff(above_half_amplitude) != 1)[0]+1)

            open_level_list = []
            for amplitude in split_index:
                if len(amplitude) > 2*length_filter:
                    open_level_list.append(amplitude[length_filter:-length_filter])

            total_open_level = self.trace[np.hstack(open_level_list)]
            self.open_level = np.mean(total_open_level)

            if p_value < 0.0001:
                print('The probability that the two baseline is the same is {:.3g}. The one which is the furtheset from the open level will be taken.'.format(p_value*100))
                baseline_1 = np.mean(baseline_1)
                baseline_2 = np.mean(baseline_2)

                if (self.open_level - baseline_1) > (self.open_level - baseline_2):
                    self.baseline = baseline_1
                else:
                    self.baseline = baseline_2
            else:
                self.baseline = np.mean([np.mean(baseline_1), np.mean(baseline_2)])




    def detect_start_stop(self, trace, open_level):
        '''
        Detect the correct time where a cluster start and stop.
        '''
        half_amplitude = np.where(trace > open_level/2)[0]

        return half_amplitude[0], half_amplitude[-1]


class Record(Segment):
    def __init__(self, filename, filter_f = 3000):
        self.filename = filename
        #TODO: currently opens Axon file directly. Make option to open SSD file.
        self.trace, self.dt = self.read_abf(self.filename)
        self.filter_rising_t = 0.3321/filter_f

    def read_abf(self, filename):
        h = dcio.abf_read_header(filename, 0)
        calfac = (1 / ((h['IADCResolution'] / h['fADCRange'])
                * h['fTelegraphAdditGain'][h['nADCSamplingSeq'][0]] *
                h['fInstrumentScaleFactor'][h['nADCSamplingSeq'][0]]))
        trace = dcio.abf_read_data(filename, h) * calfac # convert to pA
        dt = h['fADCSampleInterval'] / 1.0e6 # convert to seconds
        return trace, dt

    def slice(self, start, end, dtype = 'index'):
        start, end = sorted([start, end])
        if dtype == 'index':
            return Segment(trace = np.copy(self.trace[start: end]), dt = self.dt,
            t_start = start * self.dt, filter_rising_t = self.filter_rising_t)
        elif dtype == 'time':
            idx_start = int(np.floor(start/self.dt))
            idx_end = int(np.floor(end/self.dt))
            return Segment(trace = self.trace[idx_start: idx_end], dt = self.dt,
            t_start = start, filter_rising_t = self.filter_rising_t)


    def read(self):
        '''
        Convert the raw data to a numpy array by reading Axon files using neo.
        '''
        #from neo.io import AxonIO
        # https://github.com/NeuralEnsemble/python-neo
        # Just clone this to pythonpath
        #from quantities import kHz, ms, pA, nA, s, uV
        # https://pypi.python.org/pypi/quantities
        # Add support for units
        # Can be installed via pip
        original_file = AxonIO(filename=self.filename)
        read_data = original_file.read_block(lazy=False, cascade=True)
        self.trace = read_data.segments[0].analogsignals[0]
