import unittest

from linseed import Memory, Swap

class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.m = Memory()

    def test_total(self):
        self.assertTrue(self.m.total >= 0)

    def test_free(self):
        self.assertTrue(self.m.free >= 0)
        self.assertTrue(self.m.free <= self.m.total)

    def test_used(self):
        self.assertTrue(self.m.used >=0)
        self.assertTrue(self.m.used <= self.m.total)

    def test_percent_free(self):
        self.assertTrue(self.m.percent >= 0)
        self.assertTrue(self.m.percent <= 100)

class SwapTest(unittest.TestCase):
    def setUp(self):
        self.s = Swap()

    def test_total(self):
        self.assertTrue(self.s.total >= 0)

    def test_used(self):
        self.assertTrue(self.s.used >= 0)
        self.assertTrue(self.s.used <= self.s.total)

    def test_free(self):
        self.assertTrue(self.s.free >= 0)
        self.assertTrue(self.s.free <= self.s.total)

    def test_percent(self):
        self.assertTrue(self.s.percent >= 0)
        self.assertTrue(self.s.percent <= 100)
