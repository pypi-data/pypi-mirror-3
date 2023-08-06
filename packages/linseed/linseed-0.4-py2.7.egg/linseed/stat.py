from .read import _read

def read():
    return _read('/proc/stat')
