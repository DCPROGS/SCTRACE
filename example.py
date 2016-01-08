#! /usr/bin/env python

__author__ = "Remis"
__date__ = "$07-Jan-2016 15:26:09$"

from pylab import *

from sctrace.rawtrace import Record

if __name__ == "__main__":
    
    filename="./sctrace/samples/cluster.abf"
    cluster = Record(filename)
    end = len(cluster.trace) * cluster.dt

    t = arange(0.0, end, cluster.dt)
    print ('trace: ', cluster.trace)
    print ('time: ', t)
    plot(t, cluster.trace)
    xlabel('time (ms)')
    ylabel('Current (pA)')
    title('Cluster example')
    grid(True)
    show()
    
    
    
    
#    print(cluster.Popen(0,500))
