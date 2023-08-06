import unittest

from linseed import Batteries

class Test(unittest.TestCase):
    def test_count(self):
        Batteries.count()

class InfoTest(unittest.TestCase):
    def setUp(self):
        self.b = Batteries()

    def test_design_capacity(self):
        for b in self.b:
            x = b.info.design_capacity

    def test_last_full_capacity(self):
        for b in self.b:
            x = b.info.last_full_capacity

class StateTest(unittest.TestCase):
    def setUp(self):
        self.b = Batteries()

    def test_charging_state(self):
        for b in self.b:
            x = b.state.charging_state

    def test_remaining_capacity(self):
        for b in self.b:
            x = b.state.remaining_capacity
