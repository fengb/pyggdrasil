import math
import cmath

from . import topdown


def generate(root, algorithm=topdown, *args, **kwargs):
    """Convert a tree node into a graph using the given module.

    The module must implement the following:

    def generate(root) -> any iterable with the following requirements:
        1. Each item must be a (node, position) pair.
        2. The first node must be the root.
        3. Every position is given as complex(x, y) to simplify calculations.
        4. A position may also be None, which means do not draw. An 'empty'
           comparison should use "is None" since complex(0, 0) is valid.
        5. Every node is assumed to be size (1, 1).
    """
    return Graph(algorithm.generate(root), *args, **kwargs)


class Graph(object):
    """A graph implementation that takes a low graph.

    Graph calculates the minimum sized box (width, height) that can
    contain all of the nodes, taking into account the node size of (1, 1).

    Normalization will shift all node positions so that all of the nodes will be
    contained within the box (0, 0) and (width, height).

    Fields:
        width
        height
        radius
        padding
        normalize
        arrowlength - arrow edge length
        arrowwidth - arrow arc width in radians
    """
    def __init__(self, rawgraph, normalize=True, radius=0.5, padding=0.0,
                 arrowlength=None, arrowwidth=0.5):
        self.normalize = normalize
        self.radius = radius
        self.padding = padding
        self.arrowlength = arrowlength or padding
        self.arrowwidth = arrowwidth

        cached = list(rawgraph)

        xmin = min(pos.real for (node, pos) in cached) - 0.5
        xmax = max(pos.real for (node, pos) in cached) + 0.5
        ymin = min(pos.imag for (node, pos) in cached) - 0.5
        ymax = max(pos.imag for (node, pos) in cached) + 0.5

        self.width = self._scalar() * (xmax - xmin)
        self.height = self._scalar() * (ymax - ymin)

        self._mins = complex(xmin, ymin)
        self._nodespos = dict(cached)

    def _scalar(self):
        return 2 * (self.radius + self.padding)

    def __iter__(self):
        return iter(self._nodespos)

    def pos(self, node):
        """Return the draw position of the node."""
        if self.normalize:
            pos = self._nodespos[node] - self._mins
        else:
            pos = self._nodespos[node]
        return pos * self._scalar()

    def hasline(self, node):
        return node.parent is not None and \
           self.pos(node) is not None and self.pos(node.parent) is not None

    def linedir(self, node):
        """Return the angle (in radians) of the connecting line."""
        try:
            cpos = self.pos(node)
            ppos = self.pos(node.parent)
            vector = ppos - cpos
            return math.atan2(vector.imag, vector.real)
        except TypeError:
            return None

    def linestart(self, node):
        """Return the start position of the connecting line to the parent."""
        try:
            return self.pos(node) + self._lineoffset(node)
        except TypeError:
            return None

    def lineend(self, node):
        """Return the end position of the connecting line to the parent."""
        try:
            return self.pos(node.parent) - self._lineoffset(node)
        except TypeError:
            return None

    def _lineoffset(self, node):
        return self.radius * cmath.exp(self.linedir(node) * 1j)
