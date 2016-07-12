__author__ = "Remis"
__date__ = "$07-Jan-2016 13:20:37$"


import unittest

from sctrace.rawtrace import Record

class TestSCTrace(unittest.TestCase):

    def setUp(self):
        self.filename="./samples/cluster.abf"
        self.record = Record(self.filename)
    
    def test_Record(self):
        trace, dt = self.record.trace, self.record.dt
        self.assertTrue(dt == 0.0001)
        self.assertTrue(len(trace) == 11695)
        

    
