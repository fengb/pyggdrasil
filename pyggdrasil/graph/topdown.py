from pyggdrasil import model


def generate(root):
    return Graph(root)


class Graph(object):
    def __init__(self, node):
        self.node = node
        self.children = [Graph(child) for child in node.children]

        self._width = None

    @property
    def width(self):
        if not self._width:
            if self.children:
                self._width = sum(child.width for child in self.children)
            else:
                self._width = 1
        return self._width

    def __iter__(self):
        x = self.width / 2.0

        yield (self.node, complex(x, 0))

        offset = complex(0, 1)
        for child in self.children:
            for (node, position) in child:
                yield (node, position + offset)

            # Each child pushes following children horizontally but not
            # vertically.  position.real <=> real + 0j <=> (x, 0)
            offset = offset + child.width
