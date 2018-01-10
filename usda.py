import units
import logging
import requests
from config import USDA_API_KEY

logger = logging.getLogger(__name__)
USDA_API_BASE = 'https://api.nal.usda.gov/ndb'

# map NDB nutrient ids to names
# note: these are missing:
# - biotin (vitamin b7)
# - molybdenum
# - iodine
# - chromium
# - chloride
NUTRI_NAMES = {
    '291': 'fiber',
    '307': 'sodium',
    '203': 'protein',
    '601': 'cholesterol',
    '406': 'niacin', # vitamin B3
    '303': 'iron',
    '404': 'thiamin', # vitamin B1
    '323': 'vitamin e',
    '573': 'vitamin e',
    '435': 'folate', # vitamin B9, DFE
    '305': 'phosphorus',
    '304': 'magnesium',
    '317': 'selenium',
    '315': 'manganese',
    '421': 'choline',
    '301': 'calcium',
    '306': 'potassium',
    '401': 'vitamin c',
    '430': 'vitamin k',
    '405': 'riboflavin', # vitamin B2
    '415': 'vitamin b6',
    '418': 'vitamin b12',
    '578': 'vitamin b12',
    '410': 'pantothenic acid', # vitamin B5
    '309': 'zinc',
    '312': 'copper',
    '269': 'sugars',
    '208': 'energy',
    '205': 'carbohydrates',
    '605': 'trans fat',
    '606': 'saturated fat',
    '645': 'monounsaturated fat',
    '646': 'polyunsaturated fat',
    '320': 'vitamin a', # RAE (retinol activity equivalent). Note that for some foods only the IU measure is available.
    '328': 'vitamin d',
}
STANDARD_UNITS = {
    'fiber': 'g',
    'sodium': 'mg',
    'protein': 'g',
    'cholesterol': 'mg',
    'niacin': 'mg',
    'iron': 'mg',
    'thiamin': 'mg',
    'vitamin e': 'mg',
    'folate': 'µg',
    'phosphorus': 'mg',
    'magnesium': 'mg',
    'selenium': 'µg',
    'manganese':'mg',
    'choline': 'mg',
    'calcium': 'mg',
    'potassium': 'mg',
    'vitamin c': 'mg',
    'vitamin k': 'µg',
    'riboflavin': 'mg',
    'vitamin b6': 'mg',
    'vitamin b12': 'µg',
    'pantothenic acid': 'mg',
    'zinc': 'mg',
    'copper': 'mg',
    'sugars': 'g',
    'energy': 'kcal',
    'carbohydrates': 'g',
    'saturated fat': 'g',
    'trans fat': 'g',
    'monounsaturated fat': 'g',
    'polyunsaturated fat': 'g',
    'vitamin a': 'µg',
    'vitamin d': 'µg',
}


def usda(endpoint, data):
    return requests.post('{}{}'.format(USDA_API_BASE, endpoint), json=data, auth=(USDA_API_KEY, None))


def search_food(q):
    data = {'q': q}
    resp = usda('/search', data)
    return resp.json()['list']['item']


def lookup_nutrition(id):
    # type: [b]asic, [f]ull, or [s]tats
    data = {'ndbno': str(id), 'type': 'f'}
    resp = usda('/reports/V2', data)
    data = resp.json()['report']['food']
    return parse_nutrition(data)


def parse_nutrition(data):
    nutrients = {}
    required = list(NUTRI_NAMES.keys())
    for n in data['nutrients']:
        id = str(n['nutrient_id'])
        name = NUTRI_NAMES.get(id)
        if name is None:
            logger.debug('skipping {} ({})'.format(id, n['name']))
            continue
        required.remove(id)

        # standardize units for nutrients
        # all nutrient measurements are per 100g
        # we convert to 1g
        qty = (float(n['value'])/100, n['unit'])
        std_unit = STANDARD_UNITS[name]
        qty = units.convert(qty, std_unit)

        # merge
        if name in nutrients:
            nutrients[name]['value'] += qty[0]
        else:
            nutrients[name] = {
                'value': qty[0],
                'unit': std_unit
            }

    # assume non-specified nutrients are 0
    for id in required:
        name = NUTRI_NAMES[id]
        std_unit = STANDARD_UNITS[name]
        nutrients[name] = {
            'value': 0,
            'unit': std_unit
        }

    # measurement conversions seem to be identical
    # for all nutrients
    conversions = []
    for m in data['nutrients'][0]['measures']:
        c = [(m['eqv'], m['eunit']), (m['qty'], m['label'])]
        conversions.append(c)
    return {
        'id': data['ndbno'],
        'name': data['name'],
        'unit': data['ru'], # reporting unit
        'nutrients': nutrients,
        'conversions': conversions
    }
