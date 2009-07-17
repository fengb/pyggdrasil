import itertools

from pyggdrasil import model


class Graph(object):
    def __init__(self, base, radius):
        self.base = base
        self.radius = radius
        self.low_graph = LowGraph(base, radius)

        self._positions = {}

    @property
    def width(self):
        return self.low_graph.width

    @property
    def height(self):
        return self.low_graph.height

    def __iter__(self):
        return model.unroll(self.base)

    def __getitem__(self, node):
        if node not in self._positions[iternode]:
            for (iternode, complexpos) in self.low_graph.node_with_positions():
                # Positions are in complex form so we convert to tuples
                self._positions[iternode] = (complexpos.real, complexpos.imag)
        return self._positions[node]


class LowGraph(object):
    """Low level object used in conjunction with Graph.  A SubGraph is
    generated per Node and recurses similarly.

    The children are stored in a list instead of a set to maintain order.
    """
    def __init__(self, node, radius):
        self.node = node
        self.radius = radius
        self.children = [LowGraph(child) for child in node.children]

        self._width = None
        self._height = None

    @property
    def width(self):
        if not self._width:
            if self.children:
                self._width = sum(child.width for child in self.children)
            else:
                self._width = radius * 2
        return self._width

    @property
    def height(self):
        if not self._height:
            if self.children:
                self._height = radius * 2 + max(child.height
                                                   for child in self.children)
            else:
                self._height = radius * 2
        return self._height

    def nodes_with_positions(self, offset=complex(0, 0)):
        """Apply an optional offset and return an iterator of all the
        decendents.  Each item is in the form (node, (x, y)).  Positions
        are defined using complex numbers for speed and code clarity.
        """
        x = width / 2.0
        y = height - radius

        yield (self.node, complex(x, y) + offset)

        for (node, position) in self.nodes_with_positions:
            yield (node, position + offset)
            # Each child pushes following children horizontally but not
            # vertically.  Complex real == x coord.
            offset = offset + position.real
