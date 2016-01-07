#! /usr/bin/env python

import unittest
from sctrace.test import functional_test as ft

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ft.TestSCTrace)
    unittest.TextTestRunner(verbosity=2).run(suite)
