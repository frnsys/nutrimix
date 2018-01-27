import yaml
import numpy as np
from colorama import Fore
from mix import CON_NUTRI
from units import convert
from util import sum_quantity_key
from usda import lookup_nutrition, STANDARD_UNITS

# import logging; logging.basicConfig(level=logging.DEBUG)
ingredients = yaml.load(open('shake.yaml', 'r'))
nutritions = [lookup_nutrition(i['id']) for i in ingredients]
for i, n in zip(ingredients, nutritions):
    i.update(n)

mix = np.array([convert(i['qty'], 'g')[0] for i in ingredients])
for k, v in CON_NUTRI.items():
    amt = sum_quantity_key(ingredients, mix, 'nutrients.{}.value'.format(k))
    off_by = amt - v[0]
    percent = amt/v[0] * 100
    if off_by >= 0:
        pre = Fore.GREEN
    else:
        pre = Fore.RED
    off_by = pre + '{}{:.2f}{}'.format('+' if off_by > 0 else '', off_by, STANDARD_UNITS[k]) + Fore.RESET
    percent = pre + '{:.1f}%'.format(percent) + Fore.RESET
    print('{: >20} {: >12} {: >12} {: <22} {: >20}'.format(k, '{:.2f}{}'.format(v[0], STANDARD_UNITS[k]), '{:.2f}{}'.format(amt, STANDARD_UNITS[k]), off_by, percent))