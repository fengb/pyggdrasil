import itertools

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
        try:
            return self._parent
        except AttributeError:
            self._parent = None
            return self._parent

    def set_parent(self, value):
        if self.parent:
            self.parent.remove(self)
        if value:
            value.children.add(self)
        self._parent = value
    parent = property(get_parent, set_parent)


def unroll(node):
    """Unroll tree node and return an iterator of all the represented nodes.

    Arguments:
    node -- object must implement the method children(self) -> iterable
    """
    return itertools.chain([node], *itertools.chain(unroll(child)
                                        for child in node.children))
