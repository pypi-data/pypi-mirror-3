import logging

import pkg_resources

log = logging.getLogger(__name__)

class InfoSourceManager:
    '''A manager for the colletion of InfoSources on the system.

    This provides a dict-like interace to the available
    InfoSources. Each key in the ``InfoSourceManager`` is the name of
    an ``InfoSource``. Each value is a class object for that
    ``InfoSource``. To use an ``InfoSource``, you'll generally need to
    instantiate on of these classes.

    For example::

      mgr = InfoSourceManager()
      mem_source = mgr['linseed_memory']()
      print('percent memory used:', mem_source.percent)

    '''
    def __init__(self):
        self._sources = {}
        for p in pkg_resources.iter_entry_points('linseed.info_source'):
            try:
                p = p.load()
                self._sources[p.name()] = p
            except Exception:
                log.exception('Unable to load info-source module {}.'.format(p))

    def keys(self):
        'Iterate over the available info-source names.'
        return self._sources.keys()

    def items(self):
        'Iterate over the available info-source (name, class) tuples.'
        return self._sources.items()

    def values(self):
        'Iterate over the available info-source class objects.'
        return self._sources.values()

    def __len__(self):
        return len(self._sources)

    def __iter__(self):
        return iter(self._sources)

    def __getitem__(self, key):
        'Get an info-source class by name.'
        return self._sources[key]
