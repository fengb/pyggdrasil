from pyggdrasil import model


def generate(root):
    return Graph(root)


class Graph(object):
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

    def __iter__(self):
        x = width / 2.0
        y = height

        yield (self.node, complex(x, y))

        offset = complex(0, 0)
        for child in self.children:
            for (node, position) in child:
                yield (node, position + offset)
                # Each child pushes following children horizontally but not
                # vertically.  position.real <=> real + 0j <=> (x, 0)
                offset = offset + position.real
