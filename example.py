#! /usr/bin/env python

__author__ = "Remis"
__date__ = "$07-Jan-2016 15:26:09$"

import math
from pylab import *

from sctrace.rawtrace import Record

def display_record(t, trace):
    plot(t, trace)
    xlabel('time (ms)')
    ylabel('Current (pA)')
    title('Cluster example')
    grid(True)
    show()

if __name__ == "__main__":

    filename="./sctrace/samples/cluster.abf"
    record = Record(filename, filter_f = 3000)
    end = len(record.trace) * record.dt

    t = arange(0.0, end, record.dt)
    print ('trace: ', record.trace)
    print ('time: ', t)
    display_record(t, record.trace)

    new_segement = record.slice(0.1, 1.15, dtype = 'time')
    new_cluster = new_segement.find_cluster()
    popen = new_cluster.Popen()
    print(new_cluster)
    print(popen)
    print(new_cluster.open_level)
    #plot(new_cluster.display_trace())

    
    
    import ctypes
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    print(screensize)
    
    print('sampled points = ', len(record.trace))
    pix=screensize[0]
    block_points = math.ceil(len(record.trace) / pix)
    block_number = math.ceil(len(record.trace) / block_points)
    print('points per block = ', block_points)
    print('number of blocks = ', block_number)
    
    #temp = np.array(np.array_split(record.trace, block_number))
    #print (temp)
    t1 = []
    r1 = []
    for block, time in zip(np.array(np.array_split(record.trace, block_number)),
                           np.array(np.array_split(t, block_number))):
        t1.append(time[0])
        t1.append(time[0])
        r1.append(min(block))
        r1.append(max(block))
    #print('time=', t1)
    #print('minmax=', r1)
        
    display_record(t1, r1)