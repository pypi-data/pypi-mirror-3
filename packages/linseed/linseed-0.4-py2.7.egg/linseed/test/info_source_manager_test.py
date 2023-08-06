import unittest

from linseed import InfoSourceManager

class Test(unittest.TestCase):
    def setUp(self):
        self.mgr = InfoSourceManager()

    def test_api(self):
        self.mgr.keys()
        self.mgr.items()
        self.mgr.values()
        len(self.mgr)
        for k in self.mgr: self.mgr[k]

