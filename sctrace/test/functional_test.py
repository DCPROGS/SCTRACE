__author__ = "Remis"
__date__ = "$07-Jan-2016 13:20:37$"


import unittest


class TestSCTrace(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_import(self):
        from sctrace import rawtrace
        
    def test_example_cluster(self):
        filename="./sctrace/samples/cluster.abf"
        f = open(filename, 'rb')
        f.close()
        
    def test_rawtrace(self):
        from sctrace.rawtrace import RawRecord
        filename="./sctrace/samples/cluster.abf"
        trace = RawRecord(filename)
    
if __name__ == "__main__":
    pass
