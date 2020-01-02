class HyperEdge:
    def __init__(self, label: str, variables: set, is_atom = True):
        self._label = label
        self._variables = variables
        self._is_atom = is_atom

    def get_label(self):
        return  self._label

    def get_variables(self):
        return self._variables

    def is_atom(self):
        return self._is_atom

    def get_edge_repr(self):
        """
        Retrieve hyperedge that represents solely
        the labeled variables.

        :return:
        """
        return HyperEdge("", self._variables, False)

    def __str__(self):
        return self.get_label() + "(" + str(self._variables) + ")"