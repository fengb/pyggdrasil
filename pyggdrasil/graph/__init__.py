"""
RawGraph - any iterable with the following requirements:
    1. Each item must be a (node, position) pair.
    2. The first node must be the root.
    3. Every position is given as complex(x, y) to simplify calculations.
    4. A position may also be None, which means do not draw. An 'empty'
       comparison should use "is None" since complex(0, 0) is valid.
    5. Every node is assumed to be size (1, 1).
"""


import math
import cmath

from . import topdown


def generate(root, module=topdown, *args, **kwargs):
    """Convert a tree node into a graph using the given module.

    The module must implement the following:

    def generate(root) -> RawGraph
    """
    return Graph(module.generate(root), *args, **kwargs)


class Graph(object):
    """Reference Graph implementation that generates a Graph from a RawGraph.

    Graph calculates the minimum sized box (width, height) that can
    contain all of the nodes, taking into account the node size of (1, 1).

    Normalization will shift all node positions so that all of the nodes will be
    contained within the box (0, 0) and (width, height).

    Fields:
        normalized
        scaled
        width
        height
        radius
        padding
        arrowlength
        arrowwidth
    """
    def __init__(self, rawgraph, normalize=True, scale=True,
                 radius=0.5, padding=0.0,
                 arrowlength=None, arrowwidth=None):
        """If scale is false, node positions will not shift based upon radius
        and padding.
        """
        self.normalized = normalize
        self.scaled = scale
        self.radius = radius
        self.padding = padding
        self.arrowlength = arrowlength or padding
        self.arrowwidth = arrowwidth or padding

        scalar = 2 * (radius + padding)

        if scale:
            cached = [(node, pos*scalar) for (node, pos) in rawgraph]
        else:
            cached = list(rawgraph)

        xmin = min(pos.real for (node, pos) in cached) - 0.5*scalar
        xmax = max(pos.real for (node, pos) in cached) + 0.5*scalar
        ymin = min(pos.imag for (node, pos) in cached) - 0.5*scalar
        ymax = max(pos.imag for (node, pos) in cached) + 0.5*scalar

        self.width = xmax - xmin
        self.height = ymax - ymin

        if normalize:
            offset = complex(xmin, ymin)
            self._nodespos = dict((node, pos - offset) for (node, pos) in cached)
        else:
            self._nodespos = dict(cached)

    def __in__(self, key):
        return key in self._nodespos

    def __iter__(self):
        return iter(self._nodespos)

    def raw(self):
        """Return RawGraph equivalent of the Graph."""
        for node in self:
            yield (node, self.pos(node))

    def pos(self, node):
        """Return the draw position of the node."""
        return self._nodespos[node]

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
