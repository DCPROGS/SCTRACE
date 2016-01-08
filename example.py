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
    
    
    new_segement = cluster.slice(0, -1)
    new_cluster = new_segement.find_cluster()
    popen = new_cluster.cal_Popen()
    print(new_cluster)
    print(popen)
    print(new_cluster.open_level)
