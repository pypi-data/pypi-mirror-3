from .battery import Battery
from .cpu import CPU
from .memory import Memory, Swap
from .wicd import WICD

import pkg_resources

class Snapshot(object):
    '''A Snapshot is a quasi-dict-like mapping of info_source
    extension names to instances of the associated info_source
    extensions.

    In other words, it maps names to objects that provide different
    pieces of system information. 

    To use a Snapshot, simply instantiate one and start using it.

    TODO: The name "snapshot" is a bit misleading at this point and should probably be changed.
    '''
    def __init__(self):
        self.sources = {}
        for p in pkg_resources.iter_entry_points('linseed.info_source'):
            p = p.load()
            self.sources[p.name()] = (p, None)

    def keys(self):
        return self.sources.keys()

    def items(self):
        for k in self.keys():
            yield (k, self[k])

    def values(self):
        for k in self.keys():
            yield self[k]

    def __len__(self):
        return len(self.sources)

    def __iter__(self):
        return iter(self.sources)

    def __getitem__(self, key):
        current = self.sources[key]

        # See if we've already constructed an object of this type. If
        # not, construct one and store it.
        if current[1] is None:
            self.sources[key] = (current[0], current[0]())
            current = self.sources[key]

        # Return the instance.
        return current[1]
        
