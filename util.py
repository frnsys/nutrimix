def sum_quantity_key(d, x, key):
    """sum specified values of a list of dicts"""
    return sum(q * parse_key(d[i], key) for i, q in enumerate(x))


def parse_key(d, key):
    """access sub-keys of a dict w/ e.g. 'foo.bar.baz'"""
    for k in key.split('.'):
        d = d[k]
    return d

