#! /usr/bin/env python
"""
TraceInspector- load raw single-channel record for inspection and 
processing.
"""

import os
from math import log10, pow
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pyqtgraph as pg
from pyqtgraph.dockarea import *
import numpy as np


from sctrace.rawtrace import Record


class TraceInspector(QMainWindow):
    def __init__(self, parent=None):
        super(TraceInspector, self).__init__(parent)
        self.resize(900, 600)     # wide, high in px
        self.mainFrame = QWidget()
        self.setWindowTitle("Single-channel current trace inspector")
        area = DockArea()
        self.setCentralWidget(area)

        self.filename = None
        self.record = None
        self.path = None
        

        dock = TraceDock(self)
        area.addDock(dock, 'left')


    def update(self):
        pass
    def clear(self):
        self.filename = None
        self.trace = None
        self.seg1 = None



class TraceDock(Dock):
    def __init__(self, parent):
        super(TraceDock, self).__init__(parent)
        self.parent = parent
        #self.title = "Patch Inspector"
        #self.resize=(1, 1)
        
        
        self.seg1coor = [0,0.1]
        self.seg1 = None
        self.popen = None
        self.clusterOpenLevel = None
     
        w1 = pg.LayoutWidget()
        
        self.loadBtn = QPushButton('Load record...')
        self.clearBtn = QPushButton('Remove record and clear display')
        self.loadBtn.clicked.connect(self.load)
        self.clearBtn.setEnabled(False)
        self.clearBtn.clicked.connect(self.clear)
        w1.addWidget(self.loadBtn, row=0, col=0)
        w1.addWidget(self.clearBtn, row=0, col=1)

        self.label1 = QLabel('Displaying patch: ')
        w1.addWidget(self.label1, row=2, col=0, colspan=2)
        
        self.pltTrace = pg.PlotWidget()
        w1.addWidget(self.pltTrace, row=3, col=0, colspan=2)
        
        self.pltSegment = pg.PlotWidget()
        w1.addWidget(self.pltSegment, row=4, col=0, colspan=2)
        
        self.popenBtn = QPushButton('Calculate Popen')
        self.popenBtn.clicked.connect(self.calc_Popen)
        self.label2 = QLabel('')
        w1.addWidget(self.popenBtn, row=5, col=0)
        w1.addWidget(self.label2, row=5, col=1)

        self.addWidget(w1)
        
    def calc_Popen(self):
        cluster = self.seg1.find_cluster()
        self.popen = cluster.cal_Popen()[0]
        self.clusterOpenLevel = cluster.open_level
        self.update()
    
    
    def update(self):

        self.label1.setText('Displaying patch: ' + self.parent.filename)

        end = len(self.parent.record.trace) * self.parent.record.dt
        t = np.arange(0.0, end, self.parent.record.dt)
        if self.seg1coor == None:
            self.seg1coor = (end * 0.1, end * 0.9)
        
        self.pltTrace.clear()
        self.pltTrace.plot(t, self.parent.record.trace, pen='g')
        self.seg1StartLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        self.seg1StartLn.setValue(self.seg1coor[0])
        self.seg1StartLn.sigPositionChangeFinished.connect(self.seg1Changed)
        self.seg1EndLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        self.seg1EndLn.setValue(self.seg1coor[1])
        self.seg1EndLn.sigPositionChangeFinished.connect(self.seg1Changed)
        self.pltTrace.addItem(self.seg1StartLn)
        self.pltTrace.addItem(self.seg1EndLn)
        
        
        print('seg coordinates=', self.seg1coor)
        self.seg1 = self.parent.record.slice(self.seg1coor[0], self.seg1coor[1], dtype='time') 
        print('points in segment=', len(self.seg1.trace))
        print ('seg1 start=', self.seg1.t_start)
        print ('seg1 dt=', self.seg1.dt)
        end = self.seg1.t_start + len(self.seg1.trace) * self.seg1.dt
        print('points in segment=', len(self.seg1.trace))
        print ('points X dt =', len(self.seg1.trace) * self.seg1.dt)
        print ('end=', end)
        t = np.arange(self.seg1.t_start, end, self.seg1.dt)
        print('t:', t)
        print ('segment:', self.seg1.trace)
        self.pltSegment.clear()
        self.pltSegment.plot(t, self.seg1.trace, pen='g')
        if self.clusterOpenLevel:
            self.clusterOpenLn = pg.InfiniteLine(angle=0, movable=True, pen='r')
            self.clusterOpenLn.setValue(self.clusterOpenLevel[0])
            self.clusterOpenLn.sigPositionChangeFinished.connect(self.clusterOpenChanged)
            self.pltSegment.addItem(self.clusterOpenLn)
        
        print ('popen=', self.popen)
        
        if self.popen:
            self.label2.setText('Cluster Popen = {0:.6f}'.format(self.popen))
        
        #self.parent.update()
        
    def clusterOpenChanged(self):
        pass

    def seg1Changed(self):
        self.seg1coor = [self.seg1StartLn.value(), self.seg1EndLn.value()]
        self.update()

    def load(self):
        self.parent.filename = QFileDialog.getOpenFileName(self.parent,
            "Open single-channel record...",
            self.parent.path, 
            "Axon file (format 1.8) (*.abf *.ABF);" + 
            ";CONSAM file  (*.ssd *.SSD *.dat *.DAT);;All files (*.*)")    
        self.parent.record = Record(self.parent.filename)
        
        self.update()
        #self.parent.update()
        self.clearBtn.setEnabled(True)
        
      
    def clear(self):
        
        self.update()

        self.pltTrace.clear()
        self.pltSegment.clear()
        self.label2.setText('')
       
        self.clearBtn.setEnabled(False)

        self.parent.clear()


