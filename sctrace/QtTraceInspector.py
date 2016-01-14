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
        self.seg2 = None



class TraceDock(Dock):
    def __init__(self, parent):
        super(TraceDock, self).__init__(parent)
        self.parent = parent
        #self.title = "Patch Inspector"
        #self.resize=(1, 1)
        
        
        self.seg1coor = None
        self.seg2coor = None
        self.basecoor = None
        self.seg1 = None
        self.cluster = None
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
        
        self.pltCluster = pg.PlotWidget()
        w1.addWidget(self.pltCluster, row=5, col=0, colspan=2)
        
#        self.adjustBtn = QPushButton('Adjust baseline')
#        self.adjustBtn.clicked.connect(self.adjust_baseline)
#        self.adjustBtn.setEnabled(False)
#        w1.addWidget(self.adjustBtn, row=6, col=0)
        
        self.popenBtn = QPushButton('Calculate Popen')
        self.popenBtn.clicked.connect(self.calc_Popen)
        self.popenBtn.setEnabled(False)
        self.label2 = QLabel('')
        w1.addWidget(self.popenBtn, row=7, col=0)
        w1.addWidget(self.label2, row=7, col=1)

        self.addWidget(w1)
        
    def adjust_baseline(self):
        pass
        
    def calc_Popen(self):
        cluster = self.cluster.find_cluster()
        self.popen = cluster.cal_Popen()
        self.clusterOpenLevel = cluster.open_level
        self.update_cluster()
    
    
    def update(self):

        self.label1.setText('Displaying patch: ' + self.parent.filename)

        end = len(self.parent.record.trace) * self.parent.record.dt
        t = np.arange(0.0, end, self.parent.record.dt)
        
        # Plot all trace.
        self.pltTrace.clear()
        self.pltTrace.plot(t, self.parent.record.trace, pen='g')
        self.seg1StartLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        if self.seg1coor == None:
            self.seg1coor = (end * 0.1, end * 0.2)
        self.seg1StartLn.setValue(self.seg1coor[0])
        self.seg1StartLn.sigPositionChangeFinished.connect(self.seg1Changed)
        self.seg1EndLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        self.seg1EndLn.setValue(self.seg1coor[1])
        self.seg1EndLn.sigPositionChangeFinished.connect(self.seg1Changed)
        self.pltTrace.addItem(self.seg1StartLn)
        self.pltTrace.addItem(self.seg1EndLn)
        
        # Plot segment indicated by cursors in Trace plot.
        self.seg1 = self.parent.record.slice(self.seg1coor[0], self.seg1coor[1], dtype='time') 
        end = self.seg1.t_start + len(self.seg1.trace) * self.seg1.dt
        t = np.arange(self.seg1.t_start, end, self.seg1.dt)
        self.pltSegment.clear()
        self.pltSegment.plot(t, self.seg1.trace, pen='g')
        if self.seg2coor == None:
            self.seg2coor = (0.99*self.seg1.t_start + 0.01*end, end * 0.9)
        self.seg2StartLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        self.seg2StartLn.setValue(self.seg2coor[0])
        self.seg2StartLn.sigPositionChangeFinished.connect(self.seg2Changed)
        self.seg2EndLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        self.seg2EndLn.setValue(self.seg2coor[1])
        self.seg2EndLn.sigPositionChangeFinished.connect(self.seg2Changed)
        self.pltSegment.addItem(self.seg2StartLn)
        self.pltSegment.addItem(self.seg2EndLn)
        self.popen = None
        
        # Plot cluster indicated by cursors in Segment plot
        self.cluster = self.parent.record.slice(self.seg2coor[0], self.seg2coor[1], dtype='time')
        
        self.update_cluster()
        
    def update_cluster(self):
        end = self.cluster.t_start + len(self.cluster.trace) * self.cluster.dt
        t = np.arange(self.cluster.t_start, end, self.cluster.dt)
        self.pltCluster.clear()
        self.pltCluster.plot(t, self.cluster.trace, pen='g')
        self.baseLn = pg.InfiniteLine(angle=90, movable=True, pen='r')
        if self.basecoor == None:
            self.basecoor = 0.9*self.cluster.t_start + 0.1*end
        self.baseLn.setValue(self.basecoor)
        self.baseLn.sigPositionChangeFinished.connect(self.baseChanged)
        self.pltCluster.addItem(self.baseLn)
        
        if self.clusterOpenLevel:
            self.clusterOpenLn = pg.InfiniteLine(angle=0, movable=True, pen='y')
            self.clusterOpenLn.setValue(self.clusterOpenLevel)
            self.clusterOpenLn.sigPositionChangeFinished.connect(self.clusterOpenChanged)
            self.pltCluster.addItem(self.clusterOpenLn)
            
        if self.popen:
            self.label2.setText('Cluster Popen = {0:.6f}'.format(self.popen))
        
        #self.parent.update()
        
    
    def clusterOpenChanged(self):
        pass

    def baseChanged(self):
        self.basecoor = self.baseLn.value()
        points = int((self.basecoor - self.cluster.t_start) / self.cluster.dt)
        av = np.average(self.cluster.trace[:points])
        self.cluster.trace -= av
        self.update_cluster()
        

    def seg1Changed(self):
        coor = [self.seg1StartLn.value(), self.seg1EndLn.value()]
        self.seg1coor = np.sort(coor)
        self.update()
        
    def seg2Changed(self):
        coor = [self.seg2StartLn.value(), self.seg2EndLn.value()]
        self.seg2coor = np.sort(coor)
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
        self.popenBtn.setEnabled(True)
#        self.adjustBtn.setEnabled(True)
        
      
    def clear(self):
        
        self.update()
        self.pltCluster.clear()

        self.pltTrace.clear()
        self.pltSegment.clear()
        self.label1.setText('')
        self.label2.setText('')
       
        self.clearBtn.setEnabled(False)
        self.popenBtn.setEnabled(False)

        self.parent.clear()


