from models.HyperEdge import HyperEdge


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
        that represents the given set of variables

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

    def get_guard(self):
        return self._guard

    def get_pvar(self):
        if self._parent is not None:
            return self.get_label().get_variables().intersection(self._parent.get_label().get_variables())

        return {}

    def get_non_guards(self):
        return set(self.get_children()).difference(self._guard)

    def set_parent(self, parent):
        self._parent = parent

    def serialize(self):
        return [self.get_pvar(), [child.serialize() for child in self._children]]


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