import itertools
from collections import defaultdict

from models.HyperEdge import HyperEdge
from models.JoinTree import TreeNode, JoinTree


def _powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))


class HyperGraph:
    """
    Class that represents a hypergraph.
    """
    def __init__(self, variables: set, hyper_edges: set):
        self._variables = variables
        self._hyper_edges = hyper_edges

    def get_vertices(self):
        """
        Function to retrieve the set of vertices
        in the graph.

        :return: (set) vertices of the graph
        """
        return self._variables

    def get_edges(self):
        """
        Function to retrieve the set of edges
        in the graph.

        :return: (set) edges of the graph
        """
        return self._hyper_edges

    def get_primal_graph(self):
        """
        Function to retrieve the primal graph of the
        hypergraph.

        :return: (HyperGraph) hypergraph modeling the primal graph
        """
        edges = set()

        # Can also be achieved by looping the edges and creating combi's of the edges
        for perm in itertools.combinations(self._variables, 2):
            edge = {perm[0], perm[1]}
            for hyper_edge in self._hyper_edges:
                if edge.issubset(hyper_edge.get_variables()):
                    edges.add(frozenset(edge))
                    break

        return Graph(self._variables, edges)

    def v_adjacent(self, v: set, a, b):
        """
        Function to determine whether two edges
        are v-adjacent in the graph, given a subset
        of vertices v.

        :return: (bool) True if a is v-adjacent to b, False otherwise
        """
        for hyper_edge in self._hyper_edges:
            if {a, b}.issubset(hyper_edge.get_variables().difference(v)):
                return True

        return False

    def v_path(self, v: set, sequence: list):
        """
        Function to determine whether the given sequence if a
        v-path in the graph, given a subset of vertices v.

        :return: (bool) True if sequence is a v-path, False otherwise
        """
        for i in range(len(sequence)-1):
            if not self.v_adjacent(v, sequence[i], sequence[i+1]):
                return False

        return True

    def v_connected(self, v: set, w: set):
        """
        Function to determine whether the given subset of vertices
        w is v-connected, given a subset of vertices v.

        :return: (bool) True if w is a v-component, False otherwise
        """
        perms = itertools.combinations(w, 2)
        primal_graph = self.get_primal_graph()
        for perm in perms:
            found = False
            paths = primal_graph.gen_paths(perm[0], perm[1])

            for path in paths:
                # Verify whether path is a v-path
                if self.v_path(v, path):
                    found = True
                    break

            if not found:
                return False

        return True

    def v_component(self, v: set, w: set):
        """
        Function to determine whether the given subset of vertices
        w is a v-component, given a subset of vertices v.

        :return: (bool) True if w is a v-component, False otherwise
        """
        if not w.issubset(self._variables.difference(v)):
            return False

        if not self.v_connected(v, w):
            return False

        # Check maximality
        for var in self._variables.difference(w).difference(v):
            if self.v_connected(v, w.union(var)):
                return False

        return True

    def edges(self, c: set):
        """
        Function to retrieve the set of edges associated
        to a subset vertices of the hypergraph.

        :return: (set) set of edges
        """
        edges = set()

        for edge in self._hyper_edges:
            if c.intersection(edge.get_variables()):
                edges.add(edge)

        return edges

    def decomposable(self, c_robbers: set, marshals: set):
        """
        Function to determine whether the hyper-graph
        is 1-decomposable.

        :return: (boolean) True if 1-decomposable, False otherwise
        """
        for move in self._hyper_edges:
            # Check if robbers can't escape
            if not self._enclosed(c_robbers, marshals, move):
                continue

            # Check if robbers area decreased
            if not c_robbers.intersection(move.get_variables()):
                continue

            # Check if components can be decomposed
            valid = True
            for comp in self._gen_components(move, c_robbers):
                if not self.decomposable(comp, {move}):
                    valid = False
                    break

            if valid:
                return True

        return False

    def join_tree(self):
        """
        Function to retrieve the join tree of the hypergraph.

        :return: (JoinTree) representing the join tree
        """
        return JoinTree(self._join_tree_rec(self._variables, set()))

    def _join_tree_rec(self, c_robbers: set, marshals: set):
        """
        Function to compute the join-tree of the hypergraph.

        :return: (TreeNode) representing the root of the join tree
        """
        for move in self._hyper_edges:
            # Check if robbers can't escape
            if not self._enclosed(c_robbers, marshals, move):
                continue

            # Check if robbers area decreased
            if not c_robbers.intersection(move.get_variables()):
                continue

            # Check if components can be decomposed
            valid = True
            components = self._gen_components(move, c_robbers)
            children = []
            for comp in components:
                comp = self._join_tree_rec(comp, {move})
                if not comp:
                    valid = False
                    break

                children.append(comp)

            if valid:
                return TreeNode(move, children)

        return False

    def _gen_components(self, move: HyperEdge, c_robbers: set):
        """
        Function to generate all [move]-components.
        DISCLAIMER: Can be done way more efficiently.

        :return: (list) of [move]-components
        """
        components = []

        for comp in _powerset(self._variables):
            s_comp = set(comp)
            if self.v_component(move.get_variables(), s_comp) and s_comp.issubset(c_robbers) and len(s_comp) > 0:
                components.append(s_comp)

        return components

    def _enclosed(self, c_robbers: set, marshals, move: HyperEdge):
        """
        Function to determine whether the robbers area is enclosed by
        the marshals during the move.

        :return: (boolean) True if enclosed, false otherwise
        """
        flat_set = {item for sublist in marshals for item in sublist.get_variables()}
        for edge in self.edges(c_robbers):
            if not flat_set.intersection(edge.get_variables()).issubset(move.get_variables()):
                return False

        return True


class Graph(HyperGraph):
    """
    Class that represents a graph, i.e., a hypergraph
    with binary edges.
    """
    def __init__(self, variables: set, edges: set):
        super().__init__(variables, edges)
        self._vertex_index = defaultdict(set)
        self._prep()

    def _prep(self):
        """
        Function to create the index-structures for
        efficient graph navigation.
        """
        for edge in self._hyper_edges:
            el = iter(edge)
            a = next(el)
            b = next(el)

            self._vertex_index[a].add(b)
            self._vertex_index[b].add(a)

    def gen_paths(self, source, dest):
        """
        Function to generate all possible paths
        from source to destination, using a depth-first
        search strategy.

        :return (list) list containing all possible paths from source to dest
        """
        return self.gen_path(source, dest, [])

    def gen_path(self, current, destination, path: list):
        """
        Helper function for path generation.

        :return: (list) list containing all possible paths from source to dest
        """
        path.append(current)

        if current == destination:
            return [path]

        paths = []
        possibilities = self._vertex_index[current].difference(set(path))

        for poss in possibilities:
            res = self.gen_path(poss, destination, path[:])
            for p in res:
                paths.append(p)

        return paths