class DataNotAvailable(Exception):
    '''Thrown by plugins when they are instantiated and can not
    provide information about the system.

    For example, a WICD plugin could throw this if it's instantiated
    on a system that is not using WICD.
    '''
    pass
