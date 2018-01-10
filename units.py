UNITS = ['g', 'cal']
PREFIXES = {
    None: 1,
    'k': 1e3,
    'm': 1/1e3,
    'µ': 1/1e6,
}


def split_prefix(unit):
    if unit in UNITS:
        return None, unit
    elif unit[1:] in UNITS:
        return unit[0], unit[1:]


def scale_unit(v, p_a, p_b):
    # p_a -> _ -> p_b
    return v * PREFIXES[p_a]/PREFIXES[p_b]


def convert(qty, to_unit):
    to = to_unit
    v, frm_unit = qty
    frm_prefix, frm_unit = split_prefix(frm_unit)
    to_prefix, to_unit = split_prefix(to_unit)
    if frm_unit == to_unit:
        return scale_unit(v, frm_prefix, to_prefix), to


if __name__ == '__main__':
    qty = (10, 'g')
    converted = convert(qty, 'kg')
    assert converted[0] == 0.01
