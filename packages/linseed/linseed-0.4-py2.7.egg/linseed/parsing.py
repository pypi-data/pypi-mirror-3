# low-level parsing routines for common file formats in the proc and
# sys filesystem

def basic_parse(data):
    '''Parse whitespace-delimited data of the form "field-name val1
    val2 val3..."

    For each line in `data` of the form "field val1 val2. . .", the creates an entry in a dict
    of the form::
    
      d[field] = [val1, val2, . . .]

    This returns that dict.

    Args:
      * data: The data to parse

    Returns:
      A dict mapping from field name to lists of values.
    '''
    data = [d.split() for d in data]
    data = dict([(d[0], d[1:]) for d in data])
    return data

def paren_parse(data):
    '''Like ``basic_parse()``, but this assumes that the field-name
    ends in a ":".

    This strips off the colon, but otherwise works like ``basic_parse()``.

    Args:
      * data: The data to parse

    Returns:
      A dict mapping from field name to lists of values.
    '''
    data = [d.split(':') for d in data]
    data = [(k, v.split()) for (k,v) in data]
    return dict(data)
