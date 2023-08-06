from .exceptions import DataNotAvailable

import dbus

class Interface(object):
    def __init__(self, interface, ip):
        self._interface = interface
        self._ip = ip
        self._connected = bool(self.ip)

    @property
    def interface(self):
        'The interface ID.'
        return self._interface

    @property
    def ip(self):
        'The IP address of the interface.'
        return self._ip

    @property
    def connected(self):
        'Whether the interface is connected.'
        return self._connected

class Wireless(Interface):
    'Information for a single Wireless interface.'
    def __init__(self, proxy, iface):
        ip = proxy.GetWirelessIP(0)
        super(Wireless, self).__init__(iface, ip)

        if self.connected:
            netid = proxy.GetCurrentNetworkID(0)
            self._essid = proxy.GetWirelessProperty(netid, 'essid')
            self._quality = proxy.GetWirelessProperty(netid, 'quality')
        else:
            self._essid = ''
            self._quality = ''

    @property
    def essid(self):
        'The ESSID to which the interface is connected.'
        return self._essid

    @property
    def quality(self):
        'The quality of the connetion.'
        return self._quality

class Wired(Interface):
    'Information on a single wired interface.'
    def __init__(self, proxy, iface, idx):
        try:
            ip = proxy.wired.GetWiredIP(idx)
        except Exception:
            ip = ''

        super(Wired, self).__init__(iface, ip)

class WICD(object):
    def __init__(self):
        try:
            self.bus = dbus.SystemBus()
            self.daemon = self.bus.get_object('org.wicd.daemon', '/org/wicd/daemon')

            wireless = dbus.Interface(
                self.bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'),
                'org.wicd.daemon.wireless')
            if wireless and wireless.DetectWirelessInterface() != 'None':
                self.wireless = [Wireless(wireless, 'wifi')]
            else:
                self.wireless = []

            wired = dbus.Interface(
                self.bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wired'),
                'org.wicd.daemon.wired')
            if wired:
                self.wired = [Wired(wired, iface, idx) for (idx, iface) in enumerate(wired.GetWiredInterfaces())]
            else:
                self.wired = []

        except dbus.DBusException as e:
            raise DataNotAvailable(str(e))

    def __str__(self):
        rslt = []

        for w in self.wired:
            if w.connected:
                rslt.append('[{0}] {1}'.format(w.interface, w.ip))

        for w in self.wireless:
            if w.connected:
                rslt.append('[{0}] {1} {2}% ({3})'.format(w.interface,
                                                          w.essid,
                                                          w.quality,
                                                          w.ip))

        return ' '.join(rslt)

    @staticmethod
    def name():
        return 'linseed_wicd'

    @staticmethod
    def description():
        return 'WICD connection status'

def main():
    w = WICD()
    print(w.display())

if __name__ == '__main__':
    main()

# These are the available wicd dbus methods. It was a bit of a pain to track these down, so I'm putting them here for future reference.

# wireless:
# {u'org.freedesktop.DBus.Introspectable.Introspect': '',
#  u'org.wicd.daemon.wireless.CheckIfWirelessConnecting': '',
#  u'org.wicd.daemon.wireless.CheckWirelessConnectingMessage': '',
#  u'org.wicd.daemon.wireless.ConnectWireless': u'v',
#  u'org.wicd.daemon.wireless.CreateAdHocNetwork': u'vvvvvvv',
#  u'org.wicd.daemon.wireless.DetectWirelessInterface': '',
#  u'org.wicd.daemon.wireless.DisableWirelessInterface': '',
#  u'org.wicd.daemon.wireless.DisconnectWireless': '',
#  u'org.wicd.daemon.wireless.EnableWirelessInterface': '',
#  u'org.wicd.daemon.wireless.GetApBssid': '',
#  u'org.wicd.daemon.wireless.GetAvailableAuthMethods': u'v',
#  u'org.wicd.daemon.wireless.GetCurrentBitrate': u'v',
#  u'org.wicd.daemon.wireless.GetCurrentDBMStrength': u'v',
#  u'org.wicd.daemon.wireless.GetCurrentNetwork': u'v',
#  u'org.wicd.daemon.wireless.GetCurrentNetworkID': u'v',
#  u'org.wicd.daemon.wireless.GetCurrentSignalStrength': u'v',
#  u'org.wicd.daemon.wireless.GetIwconfig': '',
#  u'org.wicd.daemon.wireless.GetKillSwitchEnabled': '',
#  u'org.wicd.daemon.wireless.GetNumberOfNetworks': '',
#  u'org.wicd.daemon.wireless.GetOperationalMode': u'v',
#  u'org.wicd.daemon.wireless.GetWirelessIP': u'v',
#  u'org.wicd.daemon.wireless.GetWirelessInterfaces': '',
#  u'org.wicd.daemon.wireless.GetWirelessProperty': u'vv',
#  u'org.wicd.daemon.wireless.GetWpaSupplicantDrivers': '',
#  u'org.wicd.daemon.wireless.IsWirelessUp': '',
#  u'org.wicd.daemon.wireless.ReadWirelessNetworkProfile': u'v',
#  u'org.wicd.daemon.wireless.ReloadConfig': '',
#  u'org.wicd.daemon.wireless.RemoveGlobalEssidEntry': u'v',
#  u'org.wicd.daemon.wireless.SaveWirelessNetworkProfile': u'v',
#  u'org.wicd.daemon.wireless.SaveWirelessNetworkProperty': u'vv',
#  u'org.wicd.daemon.wireless.Scan': u'v',
#  u'org.wicd.daemon.wireless.SetHiddenNetworkESSID': u'v',
#  u'org.wicd.daemon.wireless.SetWirelessProperty': u'vvv'}

# wired:
# {u'org.freedesktop.DBus.Introspectable.Introspect': '',
# u'org.wicd.daemon.wired.CheckIfWiredConnecting': '',
# u'org.wicd.daemon.wired.CheckPluggedIn': '',
# u'org.wicd.daemon.wired.CheckWiredConnectingMessage': '',
# u'org.wicd.daemon.wired.ConnectWired': '',
# u'org.wicd.daemon.wired.CreateWiredNetworkProfile': u'vv',
# u'org.wicd.daemon.wired.DeleteWiredNetworkProfile': u'v',
# u'org.wicd.daemon.wired.DetectWiredInterface': '',
# u'org.wicd.daemon.wired.DisableWiredInterface': '',
# u'org.wicd.daemon.wired.DisconnectWired': '',
# u'org.wicd.daemon.wired.EnableWiredInterface': '',
# u'org.wicd.daemon.wired.GetDefaultWiredNetwork': '',
# u'org.wicd.daemon.wired.GetLastUsedWiredNetwork': '',
# u'org.wicd.daemon.wired.GetWiredIP': u'v',
# u'org.wicd.daemon.wired.GetWiredInterfaces': '',
# u'org.wicd.daemon.wired.GetWiredProfileList': '',
# u'org.wicd.daemon.wired.GetWiredProperty': u'v',
# u'org.wicd.daemon.wired.HasWiredDriver': '',
# u'org.wicd.daemon.wired.IsWiredUp': '',
# u'org.wicd.daemon.wired.ReadWiredNetworkProfile': u'v',
# u'org.wicd.daemon.wired.ReloadConfig': '',
# u'org.wicd.daemon.wired.SaveWiredNetworkProfile': u'v',
# u'org.wicd.daemon.wired.SetWiredProperty': u'vv',
# u'org.wicd.daemon.wired.UnsetWiredDefault': '',
# u'org.wicd.daemon.wired.UnsetWiredLastUsed': ''}

# daemon:
# {u'org.freedesktop.DBus.Introspectable.Introspect': '',
#  u'org.wicd.daemon.AutoConnect': u'v',
#  u'org.wicd.daemon.CancelConnect': '',
#  u'org.wicd.daemon.CheckIfConnecting': '',
#  u'org.wicd.daemon.ConnectResultsAvailable': '',
#  u'org.wicd.daemon.Disconnect': '',
#  u'org.wicd.daemon.EmitStatusChanged': u'uav',
#  u'org.wicd.daemon.FormatSignalForPrinting': u'v',
#  u'org.wicd.daemon.GetAlwaysShowWiredInterface': '',
#  u'org.wicd.daemon.GetAppAvailable': u'v',
#  u'org.wicd.daemon.GetAutoReconnect': '',
#  u'org.wicd.daemon.GetBackendDescription': u'v',
#  u'org.wicd.daemon.GetBackendDescriptionDict': '',
#  u'org.wicd.daemon.GetBackendList': '',
#  u'org.wicd.daemon.GetBackendUpdateInterval': '',
#  u'org.wicd.daemon.GetConnectionStatus': '',
#  u'org.wicd.daemon.GetCurrentBackend': '',
#  u'org.wicd.daemon.GetCurrentInterface': '',
#  u'org.wicd.daemon.GetDHCPClient': '',
#  u'org.wicd.daemon.GetDebugMode': '',
#  u'org.wicd.daemon.GetFlushTool': '',
#  u'org.wicd.daemon.GetForcedDisconnect': '',
#  u'org.wicd.daemon.GetGUIOpen': '',
#  u'org.wicd.daemon.GetGlobalDNSAddresses': '',
#  u'org.wicd.daemon.GetLinkDetectionTool': '',
#  u'org.wicd.daemon.GetNeedWiredProfileChooser': '',
#  u'org.wicd.daemon.GetPreferWiredNetwork': '',
#  u'org.wicd.daemon.GetSavedBackend': '',
#  u'org.wicd.daemon.GetShouldVerifyAp': '',
#  u'org.wicd.daemon.GetSignalDisplayType': '',
#  u'org.wicd.daemon.GetSudoApp': '',
#  u'org.wicd.daemon.GetSuspend': '',
#  u'org.wicd.daemon.GetUseGlobalDNS': '',
#  u'org.wicd.daemon.GetWPADriver': '',
#  u'org.wicd.daemon.GetWiredAutoConnectMethod': '',
#  u'org.wicd.daemon.GetWiredInterface': '',
#  u'org.wicd.daemon.GetWirelessInterface': '',
#  u'org.wicd.daemon.Hello': '',
#  u'org.wicd.daemon.NeedsExternalCalls': '',
#  u'org.wicd.daemon.ReadWindowSize': u'v',
#  u'org.wicd.daemon.SendConnectResult': '',
#  u'org.wicd.daemon.SendConnectResultsIfAvail': '',
#  u'org.wicd.daemon.SetAlwaysShowWiredInterface': u'v',
#  u'org.wicd.daemon.SetAutoReconnect': u'v',
#  u'org.wicd.daemon.SetBackend': u'v',
#  u'org.wicd.daemon.SetConnectionStatus': u'vv',
#  u'org.wicd.daemon.SetCurrentInterface': u'v',
#  u'org.wicd.daemon.SetDHCPClient': u'v',
#  u'org.wicd.daemon.SetDebugMode': u'v',
#  u'org.wicd.daemon.SetFlushTool': u'v',
#  u'org.wicd.daemon.SetForcedDisconnect': u'v',
#  u'org.wicd.daemon.SetGUIOpen': u'v',
#  u'org.wicd.daemon.SetGlobalDNS': u'vvvvv',
#  u'org.wicd.daemon.SetLinkDetectionTool': u'v',
#  u'org.wicd.daemon.SetNeedWiredProfileChooser': u'v',
#  u'org.wicd.daemon.SetPreferWiredNetwork': u'v',
#  u'org.wicd.daemon.SetShouldVerifyAp': u'v',
#  u'org.wicd.daemon.SetSignalDisplayType': u'v',
#  u'org.wicd.daemon.SetSudoApp': u'v',
#  u'org.wicd.daemon.SetSuspend': u'v',
#  u'org.wicd.daemon.SetUseGlobalDNS': u'v',
#  u'org.wicd.daemon.SetWPADriver': u'v',
#  u'org.wicd.daemon.SetWiredAutoConnectMethod': u'v',
#  u'org.wicd.daemon.SetWiredInterface': u'v',
#  u'org.wicd.daemon.SetWirelessInterface': u'v',
#  u'org.wicd.daemon.ShouldAutoReconnect': '',
#  u'org.wicd.daemon.UpdateState': '',
#  u'org.wicd.daemon.WriteWindowSize': u'vvv'}
