from models.HyperEdge import HyperEdge
from models.Relation import MultisetRelation, RelationalCatalog, RelTuple


class TreeNode:
    """
    Class that represents a node in the join tree.
    """
    def __init__(self, label: HyperEdge, children=None):
        self._label = label

        if children is None:
            children = []
        self._children = children

    def get_children(self):
        return self._children

    def get_label(self):
        return self._label

    def add_child(self, child):
        self._children.append(child)

    def contains(self, variables: set):
        """
        Function to fetch the non-atom node in the tree
        that represents the given set of variables.

        :param variables: (set) set of variables
        :return: (TreeNode) node representing the set of variables.
        """
        if not self._label.is_atom() and self._label.get_variables() == variables:
            return self

        for child in self._children:
            if child.contains(variables):
                return child

        return None

    def serialize(self):
        return [str(self._label), [child.serialize() for child in self._children]]


class GeneralizedTreeNode(TreeNode):
    def __init__(self, label: HyperEdge, children=None, guard=None, parent=None):
        super().__init__(label, children)
        self._guard = guard
        self._parent = parent

        self._lambda = None         # Live tuples
        self._psi = None            # Live tuples projected on pvar
        self._gamma = None          # Natural join of non-guards
        self._gamma_indices = []

        self._delta_lambda = None
        self._delta_psi = None
        self._delta_gamma = None

    def get_relation(self):
        return self._lambda

    def get_guard(self):
        return self._guard

    def get_pvar(self):
        if self._parent is not None:
            return frozenset(self.get_label().get_variables().intersection(self._parent.get_label().get_variables()))

        return frozenset(set())

    def get_non_guards(self):
        return set(self.get_children()).difference({self._guard})

    def set_parent(self, parent):
        self._parent = parent

    def initialize(self, catalog: RelationalCatalog):
        """
        Function to assign MultiRelations to the generalized join
        join tree, leaf nodes are assigned atoms whereas interior
        nodes are assigned projections of these atomic tables.

        :param catalog: (RelationalCatalog) wherein base tables are stored.
        """
        if len(self._children) > 0:
            for child in self._children:
                child.initialize(catalog)

            self._lambda = self._guard.get_relation().project(self._label.get_variables())
            self._gamma = self._guard._psi.copy()

            # Create non-guard indices
            for ng_child in self.get_non_guards():
                self._gamma.create_index(ng_child.get_pvar())
        else:
            self._lambda = catalog.get(self._label.get_label())

        self._psi = self._lambda.project(self.get_pvar())

    def semi_join_reduction(self):
        """
        Function to perform a bottom up semi-join reduction as defined in
        the first stage of the Yannakakis algorithm.
        """
        for child in self._children:
            child.semi_join_reduction()

        if self._parent is not None:
            self._parent._lambda = self._parent._lambda.semi_join(self._lambda)

        self._lambda.create_index(self.get_pvar())

    def enumerate(self, rel_tup: RelTuple):
        """
        Recursive function to iterate the final join results from the
        generalized join tree.

        :param rel_tup: (RelTuple)
        :return: (MultisetRelation) result of the join as computed by the join tree.
        """
        pvar = self.get_pvar()
        if len(self.get_children()) > 0:
            result = MultisetRelation("", set())
            for tup, mult in self._lambda.retrieve(pvar, rel_tup.project(pvar)).generator():
                temp = None
                for child in self._children:
                    if temp is None:
                        temp = child.enumerate(tup)
                    else:
                        temp = temp.cart_prod(child.enumerate(tup))

                # Merge results for each lookup
                result.merge(temp)

            return result

        return self._lambda.retrieve(pvar, rel_tup.project(pvar))

    def update(self, update: RelationalCatalog):
        pvar = self.get_pvar()
        for child in self._children:
            child.update(update)

        if self.get_label().is_atom():
            self._delta_lambda = update.get(self.get_label().get_label())
            self._delta_psi = self._delta_lambda.project(pvar)
        else:
            self._compute_deltas()

    def _compute_deltas(self):
        """
        Helper function to compute the deltas to apply to the materialized GRMS. Based
        on the description of the Yannakakis algorithm.

        :return:
        """
        pvar = self.get_pvar()
        self._delta_lambda = MultisetRelation("", self._label.get_variables())
        self._delta_psi = MultisetRelation("", pvar)
        self._delta_gamma = MultisetRelation("", set())
        temp = self._guard._delta_psi.copy()

        for ng_child in self.get_non_guards():
            for tup, mult in ng_child._delta_psi.generator():
                ng_child_pvar = ng_child.get_pvar()
                temp.merge(self._gamma.retrieve(ng_child_pvar, tup.project(ng_child_pvar)))

        for tup, mult in temp.generator():
            self._delta_gamma.set_multiplicity(tup, self._guard._psi.get_multiplicity(
                tup) + self._guard._delta_psi.get_multiplicity(tup) - self._gamma.get_multiplicity(tup))

            mult = 1
            for child in self._children:
                child_pvar = child.get_pvar()
                mult *= self._guard._psi.get_multiplicity(
                    tup.project(child_pvar)) + self._guard._delta_psi.get_multiplicity(tup.project(child_pvar))

            self._delta_lambda.set_multiplicity(tup, mult - self._lambda.get_multiplicity(tup))
            self._delta_psi.set_multiplicity(tup.project(pvar), self._delta_psi.get_multiplicity(
                tup.project(pvar)) + self._delta_lambda.get_multiplicity(tup))

    def apply_delta(self):
        self._lambda.add(self._delta_lambda)
        self._psi.add(self._delta_psi)

        if not self.get_label().is_atom():
            self._gamma.add(self._delta_gamma)

        for child in self._children:
            child.apply_delta()


class JoinTree:
    """
    Class that represents a join tree.
    """
    def __init__(self, root=None):
        self._root = root

    def is_empty(self):
        return self._root is not None

    def get_root(self):
        return self._root

    def set_root(self, root: TreeNode):
        """
        Function to set the root of the join tree.

        :param root: (TreeNode) root of the join tree.
        """
        self._root = root

    def contains(self, variables: set):
        """
        Function to verify whether there exists a non-atom node
        representing the given set of variables.

        :param variables: (set) set of variables.
        :return: (TreeNode) node representing the set of variables.
        """
        if self._root:
            return self._root.contains(variables)

    def serialize(self):
        """
        Function to serialize the join tree in a readable format.

        :return: (List) join-tree in a human readable format.
        """
        if self._root:
            return self._root.serialize()

        return None

    def generalize(self):
        """
        Function to transform the join tree to a generalized join tree.

        :return: (JoinTree) generalized variant of the join tree.
        """
        transformed = GeneralizedJoinTree()
        _to_generalized_join_tree(self._root, transformed, None)
        return transformed


class GeneralizedJoinTree(JoinTree):
    def __init__(self, root=None):
        super().__init__(root)

    def initialize(self, catalog: RelationalCatalog):
        if self._root:
            self._root.initialize(catalog)

    def semi_join_reduction(self):
        if self._root:
            self._root.semi_join_reduction()

    def enumerate(self):
        if self._root:
            return self._root.enumerate(RelTuple.empty())

    def update(self, update: RelationalCatalog):
        if self._root:
            self._root.update(update)
            self._root.apply_delta()


def _to_generalized_join_tree(node: TreeNode, join_tree: JoinTree, parent):
    """
    Algorithm to parse an arbitrary join tree to a generalized join tree.
    """
    if len(node.get_children()) > 0:
        child = GeneralizedTreeNode(node.get_label())
        hyper_edge = join_tree.contains(node.get_label().get_variables())

        if hyper_edge is None:
            hyper_edge = GeneralizedTreeNode(node.get_label().get_edge_repr(), guard=child, parent=parent)

            if parent is None:
                join_tree.set_root(hyper_edge)
            else:
                parent.add_child(hyper_edge)

        child.set_parent(hyper_edge)
        hyper_edge.add_child(child)

        for child in node.get_children():
            _to_generalized_join_tree(child, join_tree, hyper_edge)

    else:
        parent.add_child(GeneralizedTreeNode(node.get_label(), parent=parent))