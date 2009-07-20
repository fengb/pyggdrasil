from pyggdrasil import model


class Graph(object):
    def __init__(self, base)
        self.base = base
        self.low_graph = LowGraph(base)

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
            for (iternode, position) in self.low_graph.node_with_positions():
                self._positions[iternode] = position
        return self._positions[node]


class LowGraph(object):
    """Low level object used in conjunction with Graph.  A SubGraph is
    generated per Node and recurses similarly.

    The children are stored in a list instead of a set to maintain order.
    """
    def __init__(self, node):
        self.node = node
        self.children = [LowGraph(child) for child in node.children]

        self._width = None
        self._height = None

    @property
    def width(self):
        if not self._width:
            if self.children:
                self._width = sum(child.width for child in self.children)
            else:
                self._width = 1
        return self._width

    @property
    def height(self):
        if not self._height:
            if self.children:
                self._height = 1 + max(child.height for child in self.children)
            else:
                self._height = 1
        return self._height

    def nodes_with_positions(self):
        """Apply an optional offset and return an iterator of all the
        decendents.  Each item is in the form (node, (x, y)).
        """
        x = width / 2.0
        y = height - 0.5

        yield (self.node, complex(x, y))

        offset = complex(0, 0)
        for (node, position) in self.nodes_with_positions:
            yield (node, position + offset)
            # Each child pushes following children horizontally but not
            # vertically.  position.real <=> real + 0j <=> (x, 0)
            offset = offset + position.real
