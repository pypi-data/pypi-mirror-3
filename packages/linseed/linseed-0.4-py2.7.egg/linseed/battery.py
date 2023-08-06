'''Classes for reading batter state from the /proc filesystem on a
linux system.
'''

import glob

from . import parsing, read
from .util import pct, Quantity

class Info(object):
    '''The data in /proc/acpi/battery/BAT*/info.

    This is essentially the static information on a single battery.
    '''
    def __init__(self, id):
        try:
            self.info = Info._read(id)
        except IOError:
            raise ValueError('Unable to read info for battery {0}'.format(id))

    @property
    def design_capacity(self):
        'The design capacity for a batter.'
        return Quantity(int(self.info['design capacity'][0]),
                        self.info['design capacity'][1])

    @property
    def last_full_capacity(self):
        'The capacity of the battery the last time it was full.'
        return Quantity(int(self.info['last full capacity'][0]),
                        self.info['last full capacity'][1])

    # TODO
    # present:                 yes
    # battery technology:      rechargeable
    # design voltage:          11100 mV
    # design capacity warning: 0 mAh
    # design capacity low:     0 mAh
    # capacity granularity 1:  100 mAh
    # capacity granularity 2:  0 mAh
    # model number:            AS09D36
    # serial number:           0D36
    # battery type:            LION
    # OEM info:                SSANY

    @staticmethod
    def _read(battid):
        filename = '/proc/acpi/battery/BAT{0}/info'.format(battid)

        try:
            return read._read(
                filename,
                parsing.paren_parse)
        except IOError:
            raise ValueError(
                'Unable to read info file for battery {0}: {1}'.format(
                    battid, filename))

class State(object):
    '''The data in /proc/acpi/battery/BAT*/state.

    This is essentially the dynamic information on a single
    battery.
    '''
    def __init__(self, id):
        self.state = State._read(id)

    @property
    def charging_state(self):
        'The current charging state of a batter.'
        return self.state['charging state'][0]

    @property
    def remaining_capacity(self):
        'The current remaining capacity of a batter.'
        return Quantity(int(self.state['remaining capacity'][0]),
                        self.state['remaining capacity'][1])

    # TODO
    # present:                 yes
    # capacity state:          ok
    # present rate:            1232 mA
    # present voltage:         12375 mV

    @staticmethod
    def _read(battid):
        filename = '/proc/acpi/battery/BAT{0}/state'.format(battid)
        try:
            return read._read(
                filename,
                parsing.paren_parse)
        except IOError:
            raise ValueError(
                'Unable to read state file for battery {0}: {1}'.format(
                    battid, filename))

class Battery(object):
    '''The ACPI information for a battery.
    '''

    def __init__(self, battery_id):
        '''Construct a new Battery.

        Args:
          battery_id: The index of the battery, `0 <= battery_id <
            Batter.count`.

        Raises:
          ValueError: If `battery_id` is outside the valid range.
        '''
        self._info = Info(battery_id)
        self._state = State(battery_id)

    @property
    def info(self):
        'The static information on a battery.'
        return self._info

    @property
    def state(self):
        'The dynamic information on a battery.'
        return self._state

    def __str__(self):
        cap = pct(float(self.state.remaining_capacity.value) / self.info.last_full_capacity.value)
        if self.state.charging_state == 'discharging':
            return '{0}%-'.format(cap)
        elif self.state.charging_state == 'charging':
            return '{0}%+'.format(cap)
        else:
            return 'Full'

class Batteries(object):
    '''Implements an InfoSource battery information.
    '''

    @staticmethod
    def count():
        '''Get the number of batteries in the system.
        '''
        return len(glob.glob('/proc/acpi/battery/BAT*'))

    def __init__(self):
        self._batteries = [Battery(battid) for battid in range(Batteries.count())]

    @property
    def batteries(self):
        'A list of ``Battery`` objects for the batteries on a system.'
        return self._batteries

    def __getitem__(self, battid):
        return self.batteries[battid]

    def __len__(self):
        return len(self.batteries)

    def __iter__(self):
        return iter(self.batteries)

    def __str__(self):
        return 'Batteries({})'.format(' '.join([str(b) for b in self]))

    @staticmethod
    def name():
        return 'linseed_batteries'

    @staticmethod
    def description(short=True):
        return 'Information about the system batteries'

def main():
    print('--- Battery info ---')
    print(str(Batteries()))

if __name__ == '__main__':
    main()
