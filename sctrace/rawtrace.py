# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:59:45 2016

@author: zhiyiwu
"""

from neo.io import AxonIO
# https://github.com/NeuralEnsemble/python-neo
# Just clone this to pythonpath
from quantities import kHz, ms, pA, nA, s, uV
# https://pypi.python.org/pypi/quantities
# Add support for units
# Can be installed via pip
import numpy as np
from sklearn import mixture
# http://scikit-learn.org/stable/
# Machine learning package




class RawRecord():
    def __init__(self,filename=None, trace = None):
        '''
        read the original record.
        '''
        self.filename = filename
        self.amplitude = None
        self.temp = None
        if trace is None:
            self.read()
        else:
            self.trace = trace

    def read(self):
        '''
        Convert the raw data to a numpy array.
        '''
        original_file = AxonIO(filename=self.filename)
        read_data = original_file.read_block(lazy=False, cascade=True)
        self.trace = read_data.segments[0].analogsignals[0]

    def time2index(self, time):
        '''
        Convert the time to index.
        '''
        time = self.check_time(time)
        time = time - self.trace.t_start.rescale(ms)
        time *= self.trace.sampling_rate
        return int(np.floor(time.simplified))

    def index2time(self, index):
        '''
        Convert index to time.
        '''
        return self.trace.t_start + index * self.trace.sampling_rate



    def check_time(self, time):
        '''
        Convert the time to ms.
        '''
        try:
            time = time.rescale(ms)
        except AttributeError:
            time = time * ms
        return time

    def slice(self, start, stop):
        '''
        Generate a slice of the original record. Since the original record
        is usually too large.
        start and stop is in ms.
        '''
        idx_start, idx_stop = self.time2index(start), self.time2index(stop)

        return self.trace[idx_start: idx_stop]

    def amplitude_analysis(self):
        '''
        Analysis the baseline and conductance.
        '''
        if not self.temp is None:
            g = mixture.GMM(n_components=2)
            self.temp = np.array(self.temp)
            self.temp = np.expand_dims(self.temp, axis=1)
            e=g.fit(self.temp)
            self.amplitude = {'baseline': min(e.means_) * pA,
                              'conductance': max(e.means_)* pA}



    def detect_baseline(self):
        '''
        Detect the baseline.
        '''
        if self.amplitude is None:
            self.amplitude_analysis()
        return self.amplitude['baseline']

    def detect_conductance(self):
        '''
        TODO: Detect the baseline.
        '''
        if self.amplitude is None:
            self.amplitude_analysis()
        return self.amplitude['conductance']

    def detect_start_stop(self, start, stop, baseline, conductance):
        '''
        Detect the correct time where a cluster start and stop.
        '''
        half_amplitude = np.where(self.temp > (baseline + conductance)/2)[0]

        return half_amplitude[0], half_amplitude[-1]


    def Popen(self, start, stop, baseline = None, conductance = None,
              open_level = None, whole_cluster = False):
        '''
        Calculate the Popen in the given time.
        '''
        start, stop = self.check_time(start), self.check_time(stop)
        self.temp = self.slice(start, stop)

        if baseline is None:
            baseline = self.detect_baseline()
        if conductance is None:
            conductance = self.detect_conductance()
        if whole_cluster is False:
            idx_start, idx_stop = self.detect_start_stop(start, stop,
                                                         baseline, conductance)
        else:
            idx_start, idx_stop = self.time2index(start), self.time2index(stop)



        integrated_current = np.sum((self.trace[idx_start: idx_stop] - baseline))
        whole =  (open_level or (conductance - baseline)) * (idx_stop -idx_start)
        Popen = integrated_current/whole
        self.amplitude = None
        return Popen.simplified
        