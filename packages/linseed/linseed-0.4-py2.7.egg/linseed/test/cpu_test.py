import unittest

from linseed import CPUs

class Test(unittest.TestCase):
    def test_util(self):
        'Iterating CPU utilizations.'
        c = CPUs()
        for util in c:
            pass

    def test_interval(self):
        'CPU check interval.'
        c = CPUs(0.2)
        for util in c:
            pass