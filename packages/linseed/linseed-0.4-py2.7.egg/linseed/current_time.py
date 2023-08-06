import datetime

class CurrentTime(object):
    def __str__(self):
        return datetime.datetime.now().strftime('%c')

    def __repr__(self):
        return 'CurrentTime({})'.format(self)

    @staticmethod
    def name():
        return 'linseed_current_time'

    @staticmethod
    def description():
        return 'Current timestamp'
