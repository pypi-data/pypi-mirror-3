import unittest

from linseed import Snapshot

class Test(unittest.TestCase):
    def setUp(self):
        self.s = Snapshot()

    def test_api(self):
        self.s.keys()
        self.s.items()
        self.s.values()
        len(self.s)
        for k in self.s: self.s[k]
        
