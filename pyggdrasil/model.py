import itertools


class NodeParseException(Exception): pass


class Node(object):
    """A single node of a tree. The tree is bidirectional: having a reference to
    both the parent and the children.

    When setting parent, the class will automatically set the corresponding
    children. (This does not happen when operating on children).
    """
    def __init__(self, id, data, parent=None):
        # Needed to prevent self.parent=  from exploding
        self._parent = None

        self.id = id
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

    def raw(self, renameme=None):
        """"""
        if renameme is None:
            renameme = {'nodes': {}, 'data': {}}

        if self.parent:
            renameme['nodes'][self.id] = self.parent.id
        else:
            renameme['nodes'][self.id] = None
        renameme['data'][self.id] = self.data
        for child in self.children:
            child.raw(renameme)

        return renameme

    @classmethod
    def from_raw(cls, raw):
        nodes = {}
        for (id, data) in raw['data'].items():
            nodes[id] = cls(id, data)

        for (id, parent_id) in raw['nodes'].items():
            if parent_id:
                nodes[id].parent = nodes[parent_id]

        roots = [node for node in nodes.values() if not node.parent]
        if len(roots) != 1:
            raise NodeParseException(raw)

        return roots[0]


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

