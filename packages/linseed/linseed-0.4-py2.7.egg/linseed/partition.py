import psutil

class Partition:
    'Information on a single partition.'

    def __init__(self, info):
        self._info = info
        self._usage = psutil.disk_usage(self.mount_point)

    @property
    def device(self):
        'The device holding this partition.'
        return self._info.device

    @property
    def mount_point(self):
        'The mount point for this partition.'
        return self._info.mountpoint

    @property
    def type(self):
        'The type of filesystem for this partition.'
        return self._info.fstype

    @property
    def usage(self):
        'Usage statistics for this partition.'
        return self._usage

    def __str__(self):
        return 'Partition(device={}, mount_point={}, type={}, usage={})'.format(
            self.device,
            self.mount_point,
            self.type,
            self.usage)

    def __repr__(self):
        return 'Partition(device={}, mount_point={}, type={}, usage={})'.format(
            self.device,
            self.mount_point,
            self.type,
            self.usage)

class Partitions:
    'The collection of partitions mounted on the system.'
    def __init__(self):
        self._partitions = [Partition(i) for i in psutil.disk_partitions()]

    @property
    def partitions(self):
        'A list of Partition instances for the partitions in the system.'
        return self._partitions

    def __iter__(self):
        return iter(self.partitions)

    @staticmethod
    def name():
        return 'linseed_partitions'

    @staticmethod
    def description(short=True):
        return 'Partition information'

    def __str__(self):
        return str(self.partitions)


