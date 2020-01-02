from collections import Counter
from frozendict import frozendict


# Sources:
#  - https://docs.python.org/3.1/library/collections.html#collections.Counter
#  - https://docs.python.org/3/library/collections.html#collections.namedtuple
class RelTuple:
    def __init__(self, attr_map=None):
        if attr_map is None:
            attr_map = {}
        self._attr_map = frozendict(attr_map)

    def project(self, variables: set):
        proj = {}
        for var in variables:
            proj[var] = self._attr_map[var]

        return RelTuple(frozendict(proj))

    def __str__(self):
        return str(self._attr_map)

    def __eq__(self, other):
        if not isinstance(other, RelTuple):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._attr_map == other._attr_map

    def __hash__(self):
        return hash(self._attr_map)


class MultisetRelation:
    def __init__(self, name, variables, tuples=None):
        if tuples is None:
            tuples = []

        self._name = name
        self._variables = variables
        self._cnt = Counter()
        self.add(tuples)

    def get_variables(self):
        return self._variables

    def get_name(self):
        return self._name

    def add(self, tuples: list):
        self._cnt.update(tuples)

    @staticmethod
    def from_file(name, file):
        tuples = []
        f = open(file, "r")
        header = None
        for line in f:
            if header is None:
                header = line.split(" ")

            else:
                val = line.split(" ")
                tuples.append(RelTuple(dict(zip(header, val))))

        return MultisetRelation(name, set(header), tuples)


class Catalog:
    def __init__(self):
        self._catalog = {}

    def add(self, relation: MultisetRelation):
        self._catalog[relation.get_name()] = relation

    def get(self, name: str):
        return self._catalog[name]