import unittest

from linseed import WICD

class Test(unittest.TestCase):
    def setUp(self):
        self.wicd = WICD()

    def test_wireless(self):
        self.wicd.wireless

    def test_wireless_interface(self):
        for w in self.wicd.wireless:
            w.interface

    def test_wireless_ip(self):
        for w in self.wicd.wireless:
            w.ip

    def test_wireless_connected(self):
        for w in self.wicd.wireless:
            w.connected

    def test_wireless_essid(self):
        for w in self.wicd.wireless:
            w.essid

    def test_wireless_quality(self):
        for w in self.wicd.wireless:
            w.quality

    def test_is_wired(self):
        self.wicd.wired

    def test_wired_interface(self):
        for w in self.wicd.wired:
            w.interface

    def test_wired_ip(self):
        for w in self.wicd.wired:
            w.ip

    def test_wired_connected(self):
        for w in self.wicd.wired:
            w.connected

    def test_str(self):
        str(self.wicd)
