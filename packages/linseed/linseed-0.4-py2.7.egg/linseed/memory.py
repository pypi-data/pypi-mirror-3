import psutil

class Memory(object):
    '''Information on the state of main memory for a system.
    '''
    def __init__(self):
        self._usage = psutil.phymem_usage()

    @property
    def total(self):
        'Total physical memory.'
        return self._usage.total

    @property
    def used(self):
        'Memory currently in use.'
        return self._usage.used

    @property
    def free(self):
        'Memory currently free.'
        return self._usage.free

    @property
    def percent(self):
        'Percent of memory currently in use.'
        return self._usage.percent

    @staticmethod
    def name():
        return 'linseed_memory'

    @staticmethod
    def description():
        return 'Current memory utilization (%)'

    def __str__(self):
        return 'Memory(total={}, used={}, free={}, percent={})'.format(
            self.total,
            self.used,
            self.free,
            self.percent)

class Swap(object):
    def __init__(self):
        self._usage = psutil.virtmem_usage()

    @property
    def total(self):
        'Total swap space.'
        return self._usage.total

    @property
    def used(self):
        'Swap currently in use.'
        return self._usage.used

    @property
    def free(self):
        'Swap currently free.'
        return self._usage.free

    @property
    def percent(self):
        'Percent of swap currently in use.'
        return self._usage.percent

    @staticmethod
    def name():
        return 'linseed_swap'

    @staticmethod
    def description():
        return 'Current swap usage (%)'

    def __str__(self):
        return 'Swap(total={}, used={}, free={}, percent={})'.format(
            self.total,
            self.used,
            self.free,
            self.percent)