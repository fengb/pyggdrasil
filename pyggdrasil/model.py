import itertools

class Node(object):
    """A single node of a tree. The tree is bidirectional: having a reference to
    both the parent and the children.

    When setting parent, the class will automatically set the corresponding
    children. (This does not happen when operating on children).
    """
    def __init__(self, data, parent=None):
        # Needed to prevent self.parent=  from exploding
        self._parent = None

        self.data = data
        self.children = []
        self.parent = parent

    def get_parent(self):
        return self._parent

    def set_parent(self, value):
        if self.parent:
            self.parent.children.remove(self)
        if value:
            value.children.append(self)
        self._parent = value
    parent = property(get_parent, set_parent)


def unroll(node):
    """Unroll tree node and return an iterator of all the represented nodes.
    Order is defined as current node, then children, then children's children,
    etc., with children having same order as the data structure.

    Arguments:
    node -- object must implement the method children(self) -> iterable
    """
    yield node

    childreniters = [unroll(child) for child in node.children]

    # Grab children manually
    for iter in childreniters:
        yield iter.next()

    # Iterators should only contain non-children descendents now
    for iter in childreniters:
        for item in iter:
            yield item

