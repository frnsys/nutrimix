this treats the creation of a cheap, nutritional shake as a constrained optimization problem, where you want to:

- minimize the cost of each shake
- meet some minimum nutritional content targets
- under some maximum shake size (currently 18oz)

notes:

- get a USDA NDB API key from: <https://ndb.nal.usda.gov/ndb/doc/index>
- add ingredients to `ingredients.yaml` in the format:
```
- id: '<NDB id>'
  cost: <cost/g>
```
- to search for a food: `python search.py "<QUERY>"`
    - the USDA NDB has multiple entries for many foods with varying quality of information, so make sure you pick one with as much info as possible. You can check at <https://ndb.nal.usda.gov/ndb/search/list>
- to generate a mix: `python mix.py`