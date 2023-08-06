import psutil

class CPUs:
    '''Provides information on CPU utilization.

    Args:
      interval: The interval in seconds over which to measure CPU
        utilization.

    '''

    def __init__(self, interval=0.1):
        self._utilizations = psutil.cpu_percent(interval=interval, percpu=True)

    @property
    def utilizations(self):
        'A list of CPU utilizations measurements.'
        return self._utilizations

    def __iter__(self):
        return iter(self.utilizations)

    @staticmethod
    def name():
        return 'linseed_cpus'

    @staticmethod
    def description(short=True):
        return 'CPU utilization information'

    def __str__(self):
        return 'CPUs(utilizations={})'.format(self.utilizations)

def main():
    print('--- CPU info ---')
    print(str(CPUs(0.1)))

if __name__ == '__main__':
    main()
