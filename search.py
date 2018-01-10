"""
search foods by name and get nutritional database ids
"""

import sys
from usda import search_food

q = sys.argv[1]
for food in search_food(q):
    print('[{}] {}'.format(food['ndbno'], food['name'].title()))
