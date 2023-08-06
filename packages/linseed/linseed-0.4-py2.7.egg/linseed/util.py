def pct(val):
    '''Convert a value to an integer percentage.
    '''
    return int(val * 100)

def div(num, den):
    '''A "safe" divide which returns 0 on zero-division.
    '''
    try:
        return float(num) / den
    except ZeroDivisionError:
        return 0

class Quantity(object):
    '''A value along with its units.

    Args:
      * value: The numeric value of the quantity.
      * unit: The units of the quantity (string).
    '''
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit
