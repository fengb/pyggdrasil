class Node(object):
    """A single node of a tree. The tree is bidirectional: having a reference to
    both the parent and the children.

    When setting parent, the class will automatically set the corresponding
    children. (This does not happen when operating on children).
    """
    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        self.children = set()

    def get_parent(self):
        return self._parent

    def set_parent(self, value):
        if self.parent:
            self.parent.remove(self)
        if value:
            value.children.add(self)
        self._parent = value
    parent = property(get_parent, set_parent)


class Graph(object):
    """Interface for a graph.

    Fields
    ---
    radius - the preconfigured node radius used for generation
    width - the width of the entire graph
    height - the height of the entire graph
    """
    def __init__(self, base, radius):
        """
        base - the base node
        radius - the radius to use for each node
        """

    def __iter__(self):
        """Iterate through all the nodes."""

    def __getitem__(self, node):
        """Grab the position of the node.

        Position is in the the format (x, y)
        """
