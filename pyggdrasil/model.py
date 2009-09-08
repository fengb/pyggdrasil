import operator

from . import validate


class CircularTreeException(Exception): pass


def chain(func1, func2):
    return lambda x: func1(func2(x))


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

    def getparent(self):
        return self._parent

    def setparent(self, value):
        if value and value.hasancestor(self):
            raise CircularTreeException
        if self.parent:
            self.parent.children.remove(self)
        if value:
            value.children.append(self)
        self._parent = value
    parent = property(getparent, setparent)

    def unroll(self):
        """Unroll tree node and return an iterator of all the represented nodes.
        Order is defined as current node, then children, then children's
        children, etc., with children having same order as the data structure.
        """
        yield self

        childreniters = [child.unroll() for child in self.children]

        # Grab children manually
        for iter in childreniters:
            yield iter.next()

        # Iterators should only contain non-children descendents now
        for iter in childreniters:
            for item in iter:
                yield item

    def sort(self, key=None):
        if key:
            self.children.sort(key=chain(key, operator.attrgetter('id')))
        else:
            self.children.sort(key=operator.attrgetter('id'))

    def hasancestor(self, node):
        if not self.parent:
            return False
        if node == self.parent:
            return True

        return self.parent.hasancestor(node)


class EqualsDict(object):
    """Data structure to emulate a dict.

    Allow the use of non-hashables as key but performance is very slow.
    """
    def __init__(self):
        self._items = []

    def __getitem__(self, key):
        for item in self._items:
            if item[0] == key:
                return item[1]

        raise KeyError(key)

    def __setitem__(self, key, value):
        for item in self._items:
            if item[0] == key:
                item[1] = value
                break
        else:
            self._items.append([key, value])

    def __delitem__(self, key):
        self.pop(key)

    def pop(self, key):
        for (i, item) in enumerate(self._items):
            if item[0] == key:
                item = self._items.pop(i)
                return item[1]

        raise KeyError(key)

    def getkey(self, value):
        for item in self._items:
            if item[1] == value:
                return item[0]

        raise KeyError(value)


def Options(values={}):
    options = validate.ValidationDict([
        ('tree', [
            ('sort', validate.Bool(True)),
        ]),
        ('graph', [
            ('radius', validate.Float(40, min=1)),
            ('padding', validate.Float(5, min=0)),
            ('arrow_length', validate.Float(5, min=0)),
            ('arrow_width', validate.Float(5, min=0)),
        ]),
    ])
    options.load(values)
    return options
