#! /usr/bin/env python

__author__ = "Remis"
__date__ = "$07-Jan-2016 15:26:09$"

from pylab import *

from sctrace.rawtrace import Trace

if __name__ == "__main__":
    
    filename="./sctrace/samples/cluster.abf"
    cluster = Trace(filename)
    print ('dt=', cluster.dt)
    
    
    #cluster = RawRecord(filename)
    #print('sampling rate =', 1e6 / cluster.trace.sampling_rate, ' us')
    #print('number of points =', len(cluster.trace))
    #print('end_time =', (len(cluster.trace) / cluster.trace.sampling_rate))
    
    #t = arange(0.0, end_time, 1 / cluster.trace.sampling_rate)
    plot(cluster.trace)
    xlabel('time (ms)')
    ylabel('Current (pA)')
    title('Cluster example')
    grid(True)
    show()
    
    
    
    
    #print(cluster.Popen(0,500))
