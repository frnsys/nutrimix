import yaml
import numpy as np
from util import sum_quantity_key
from scipy.optimize import minimize
from usda import lookup_nutrition, STANDARD_UNITS


# based on nutrition of OPTIFAST 800 shake mix
# in the relevant nutrient's standard units
CON_NUTRI = {
    'energy': (300, None),
    'fiber': (3, None),
    'protein': (16, None),
    'iron': (3, None),
    'vitamin a': (180, None),
    'vitamin e': (3, None),
    'vitamin d': (4, None),
    'thiamin': (0.24, None),
    'niacin': (3.2, None),
    'folate': (80, None),
    'phosphorus': (310, None),
    'magnesium': (85, None),
    'selenium': (11, None),
    'manganese': (0.46, None),
    'choline': (20, None),
    'calcium': (260, None),
    'potassium': (720, None),
    'vitamin c': (18, None),
    'vitamin k': (24, None),
    'riboflavin': (0.26, None),
    'vitamin b6': (0.34, None),
    'vitamin b12': (0.48, None),
    'pantothenic acid': (1, None),
    'zinc': (2.2, None),
    'copper': (0.18, None),
}
MAX_MASS = 520 # in g
MAX_INGREDIENT_MASS = 100 # in g

# cost is in $/g
ingredients = yaml.load(open('ingredients.yaml', 'r'))
nutritions = [lookup_nutrition(i['id']) for i in ingredients]
for i, n in zip(ingredients, nutritions):
    i.update(n)

with open('ingredients.yaml', 'w') as f:
    yaml.dump(ingredients, f, default_flow_style=False)


def objective(x):
    """objective is to minimize cost"""
    return sum_quantity_key(ingredients, x, 'cost')


def mass_constraint(x):
    return MAX_MASS - sum(x)



if __name__ == '__main__':
    # generate bounds (all non-negative) and initial guesses
    guess = np.array([1 for _ in ingredients])
    bounds = [(0, MAX_INGREDIENT_MASS) for _ in guess]

    # generate minimum nutrition constraints
    # 'ineq' -> looks for >= 0
    # 'eq' -> looks for == 0
    nutri_constraints = []
    for k, (l, u) in CON_NUTRI.items():
        if l is not None:
            nutri_constraints.append({
                'type': 'ineq',
                'fun': lambda x, l=l: sum_quantity_key(ingredients, x, 'nutrients.{}.value'.format(k)) - l
            })
        if u is not None:
            nutri_constraints.append({
                'type': 'ineq',
                'fun': lambda x, u=u: u - sum_quantity_key(ingredients, x, 'nutrients.{}.value'.format(k))
            })

    # optimize
    results = minimize(objective, x0=guess, bounds=bounds, constraints=[
        {'type': 'ineq', 'fun': mass_constraint},
    ] + nutri_constraints, method='SLSQP')

    # print results
    mix = results['x']
    print('--mix--')
    for i, q in enumerate(mix):
        ingredient = ingredients[i]
        print('{} -> {:.2f} {}'.format(ingredient['name'], q, ingredient['unit']))

    print('--nutritional content--')
    for k, v in CON_NUTRI.items():
        amt = sum_quantity_key(ingredients, mix, 'nutrients.{}.value'.format(k))
        off_by = amt - v[0]
        off_by = '{}{:.2f}{}'.format('+' if off_by > 0 else '', off_by, STANDARD_UNITS[k])
        print('{: >20} {: >8} {: <8}'.format(k, '{:.2f}{}'.format(amt, STANDARD_UNITS[k]), off_by))

    print('total cost: ${:.2f}'.format(sum_quantity_key(ingredients, mix, 'cost')))
