from collections import namedtuple

Size = namedtuple('Size', 'gigabytes bytes')
size_pat = re.compile('^([0-9.]+)([a-zA-Z]+)$')
def size_parser(string):
    m = size_pat.match(string)
    if m is None:
        raise ValueError('Value %s could not be parsed to a size' + \
                             ' (something like 10Kb, or 1Mb could have).' % string)
    digits, units = m.groups()
    try:
        digits = float(digits)
    except ValueError:
        raise ValueError('Value %s could not be parsed to a size' + \
                             ' (something like 10Kb, or 1Mb could have).' % string)
        
    if units == 'b':
        modifier = 1
    elif units == 'Kb':
        modifier = 1E3
    elif units == 'Mb':
        modifier = 1E6
    elif units == 'Gb':
        modifier = 1E9
    else:
        raise ValueError('Value %s could not be parsed to a size' + \
                             ' (something like 10Kb, or 1Mb could have).')
    size = 1.0 * digits * modifier
    return Size(int(size / 1E9), int(size % 1E9))
