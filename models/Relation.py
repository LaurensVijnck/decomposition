from collections import Counter, defaultdict
from frozendict import frozendict


# Sources:
#  - https://docs.python.org/3.1/library/collections.html#collections.Counter
#  - https://docs.python.org/3/library/collections.html#collections.namedtuple
class RelTuple:
    """
    Class that represents a relational tuple.
    """
    def __init__(self, attr_map=None):
        if attr_map is None:
            attr_map = {}
        self._attr_map = frozendict(attr_map)

    def get_attributes(self):
        return self._attr_map

    def project(self, variables: set):
        """
        Function to project the tuple on the given set of variables.

        :param variables: (set) variables to project on.
        :return: (RelationTuple) obtained by projecting on given set of variables.
        """
        proj = {}
        for var in variables:
            proj[var] = self._attr_map[var]

        return RelTuple(frozendict(proj))

    def join(self, tuple):
        """
        Function to join the tuple with the given RelTuple.

        :param tuple: (RelTuple) to join with
        :return:  (RelTuple) obtained by joining with tuple
        """
        tup = RelTuple()
        tup._attr_map = frozendict({**self._attr_map, **tuple.get_attributes()})
        return tup

    @staticmethod
    def empty():
        return RelTuple(frozendict({}))

    def __str__(self):
        return str(list(self._attr_map.items()))

    def __eq__(self, other):
        if not isinstance(other, RelTuple):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._attr_map == other._attr_map

    def __hash__(self):
        return hash(self._attr_map)


class MultisetRelation:
    """
    Class that represents a multiset of relational tuples.
    """
    def __init__(self, name, variables: set, tuples=None):
        if tuples is None:
            tuples = []

        self._name = name
        self._variables = variables
        self._cnt = Counter()
        self._index = None
        self.add(tuples)

    def get_variables(self):
        return self._variables

    def get_name(self):
        return self._name

    def add(self, tuples: list):
        self._cnt.update(tuples)

    def copy(self):
        rel = MultisetRelation(self._name, self._variables)
        for tup, mult in self._cnt.items():
            rel._cnt[tup] = mult

        return rel

    def print(self):
        for tup, mult in self._cnt.items():
            print(str(tup), mult)

    def generator(self):
        """
        Generator to iterate the tuples in the MultisetRelation.

        :return: (Generator) iterating the tuples in the GMR
        """
        for tup, mult in self._cnt.items():
            yield tup, mult

    def project(self, variables: set):
        """
        Function to project the tuples in the multiset onto the
        given set of variables.

        :param variables: (set) variables to project on.
        :return: (MultisetRelation) obtained by projecting tuples on given set of variables.
        """
        rel = MultisetRelation("", variables)
        for tup, mult in self._cnt.items():
            rel._cnt[tup.project(variables)] = mult

        return rel

    def merge(self, right):
        """
        Function to obtain new GMR by merging the current one with the given relation.

        :param right: (MultisetRelation) to merge with.
        :return: (MultisetRelation) obtained by merging
        """
        rel = MultisetRelation("", self._variables)
        for tup, mult in self._cnt.items():
            rel._cnt[tup] = mult

        for tup, mult in right.generator():
            rel._cnt[tup] = mult

        return rel

    def cart_prod(self, right):
        """
        Function to compute carthesian product with current GMR with the given GMR.

        :param right: (MultisetRelation) to join with
        :return: (MultisetRelation) obtained by joining
        """
        rel = MultisetRelation("", self._variables.union(right.get_variables()))
        for l_tup, l_mult in self._cnt.items():
            for r_tup, r_mult in right.generator():
                rel._cnt[l_tup.join(r_tup)] = l_mult * r_mult

        return rel

    def semi_join(self, right):
        """
        Function to perform a left semi-join with the given relation.

        :param right: (MultisetRelation) to semi-join with.
        :return: (MultisetRelation) obtained by performing left-semi join with right.
        """
        rel = MultisetRelation("", self._variables)
        join_vars = self._variables.intersection(right.get_variables())
        projected = right.project(join_vars)
        for tup, mult in self._cnt.items():
            right_mult = projected.get_multiplicity(tup.project(join_vars))
            if right_mult > 0:
                rel._cnt[tup] += mult * right_mult

        return rel

    def get_multiplicity(self, rel_tuple: RelTuple):
        """
        Function to retrieve the multiplicity of the given RelationalTuple
        in the MultisetRelation.

        :param rel_tuple: (RelTuple) to obtain the multiplicity of.
        :return: (Number) representing the multiplicity of the tuple.
        """
        return self._cnt[rel_tuple]

    def create_index(self, variables: set):
        """
        Function to create an index of the MultisetRelation on the given set of variables.

        :param variables: (set) variables to create the index on
        """
        self._index = defaultdict(list)
        for tup, mult in self._cnt.items():
            self._index[tup.project(variables)].append([tup, mult])

    def retrieve(self, rel_tuple: RelTuple):
        """
        Function to retrieve tuples that match the given rel_tuple, making
        use of the index.

        :param rel_tuple: (RelTuple) to match tuples against
        :return: (MultisetRelation) of matching tuples
        """
        rel = MultisetRelation("", self._variables)
        for tup, mult in self._index[rel_tuple]:
            rel._cnt[tup] = mult

        return rel

    @staticmethod
    def from_file(name, file):
        """
        Function to read a MultisetRelation from a file. Function assumes
        that the first line represents the header of the relation, i.e., it
        should specify the variables that the relation defines.

        :param name: (String) name of the MultisetRelation.
        :param file: (String) path to the file representing the MultisetRelation.
        :return: (MultisetRelation) as read from the file.
        """
        tuples = []
        f = open(file, "r")
        header = None
        for line in f:
            if header is None:
                header = line.replace("\n", "").split(" ")

            else:
                val = line.replace("\n", "").split(" ")
                tuples.append(RelTuple(dict(zip(header, val))))

        return MultisetRelation(name, set(header), tuples)


class RelationalCatalog:
    """
    Class that represents a database of MultisetRelations, i.e., a mapping
    from names to MultisetRelations.
    """
    def __init__(self):
        self._catalog = {}

    def add(self, relation: MultisetRelation):
        self._catalog[relation.get_name()] = relation

    def get(self, name: str):
        return self._catalog[name]