import itertools

from models.HyperGraph import HyperGraph


def v_adjacent(hypergraph: HyperGraph, v: set, x, y):
    """
    Function to determine whether x is [v]-adjacent to y.

    :param hypergraph: (HyperGraph) hypergraph to consider
    :param v: (Set) set of variables
    :param x: (Variable) start variable
    :param y: (Variable) end variable
    :return: True if x is [v]-adjacent to y, False otherwise
    """
    for edge in hypergraph.get_edges():
        if {x, y}.issubset(edge.difference(v)):
            return True

    return False


def v_path(hypergraph: HyperGraph,  v: set, path):
    for i in range(len(path)-1):
        if not v_adjacent(hypergraph, v, path[i], path[i+1]):
            return False

    return True


def v_connected(hypergraph: HyperGraph,  v, variables):
    for pair in itertools.combinations(variables, 2):
        found = False
        perms = itertools.permutations(hypergraph.get_variables())
        for perm in perms:
            if perm[0] == pair[0] and perm[-1] == pair[1]:
                if v_path(hypergraph, v, perm):
                    found = True
                    break

        if not found:
            return False

    return True


def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))


def main():
    variables = {'A', 'B', 'C', 'D'}
    edges = {frozenset({'A', 'B'}), frozenset({'C', 'D'})}
    graph = HyperGraph(variables, edges)

    pow = powerset(variables)
    for v in pow:
        sub = powerset(variables.difference(v))
        if v_connected(graph, v, sub):
            print(v)
            print(list(sub))


if __name__ == "__main__":
    main()