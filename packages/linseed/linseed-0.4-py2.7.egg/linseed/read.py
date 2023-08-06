from . import parsing

def _read(filename, parser=parsing.basic_parse):
    '''Read a file and return the parsed results.

    Args:
      * filename: The name of the file to read.
      * parser: The parser to use (see ``parsing`` module.)

    Returns:
      The output of ``parser``.
    '''
    with open(filename, 'r') as f:
        return parser(list(f))

