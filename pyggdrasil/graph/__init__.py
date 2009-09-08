"""
RawGraph - any iterable with the following requirements:
    1. Each item must be a (node, position) pair.
    2. Every position is given as complex(x, y) to simplify calculations.
    3. A position may also be None, which means do not draw. An 'empty'
       comparison should use "is None" since complex(0, 0) is valid.
    4. Every node is assumed to be size (1, 1).
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
        width
        height
        radius
        padding

        arrow_length
        arrow_width
        arrow_points
    """
    def __init__(self, rawgraph, normalize=True,
                 radius=0.5, padding=0.0,
                 arrow_length=None, arrow_width=None):
        self.normalized = normalize
        self.radius = radius
        self.padding = padding
        self.arrow_length = arrow_length or padding
        self.arrow_width = arrow_width or padding

        self._basearrow_points = [
            0j,
            -self.arrow_length + 1j*self.arrow_width/2.0,
            -self.arrow_length - 1j*self.arrow_width/2.0,
        ]

        scalar = 2 * (radius + padding)

        cached = [(node, _round(pos*self._scalar(), 10)) for (node, pos) in rawgraph]

        xmin = min(pos.real for (node, pos) in cached) - 0.5*self._scalar()
        xmax = max(pos.real for (node, pos) in cached) + 0.5*self._scalar()
        ymin = min(pos.imag for (node, pos) in cached) - 0.5*self._scalar()
        ymax = max(pos.imag for (node, pos) in cached) + 0.5*self._scalar()

        self.width = xmax - xmin
        self.height = ymax - ymin

        if normalize:
            offset = complex(xmin, ymin)
            self._nodespos = dict((node, pos - offset) for (node, pos) in cached)
        else:
            self._nodespos = dict(cached)

    def _scalar(self):
        return 2.0 * (self.radius + self.padding)

    def __in__(self, key):
        return key in self._nodespos

    def __iter__(self):
        return iter(self._nodespos)

    def raw(self):
        """Return RawGraph equivalent of the Graph.
        """
        for node in self:
            yield (node, self.pos(node) / self._scalar())

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

    def arrow_points(self, node):
        """Return the points for the arrow."""
        direction = 1j * self.linedir(node)
        offset = self.lineend(node)
        return [pos * cmath.exp(direction) + offset
                    for pos in self._basearrow_points]

    def _lineoffset(self, node):
        return self.radius * cmath.exp(self.linedir(node) * 1j)

    def scale(self, value):
        """Multiply each position by value.
        Also scales radius, padding, width, and height.
        """
        return Graph(self.raw(),
                     radius=self.radius*value, padding=self.padding*value,
                     arrow_width=self.arrow_width*value, arrow_length=self.arrow_length*value)


def transition(startgraph, endgraph, endweight):
    startraw = dict(startgraph.raw())
    endraw = dict(endgraph.raw())
    startweight = 1 - endweight

    nodespos = []
    nodes = set(startraw) | set(endraw)
    for node in nodes:
        startpos = _ancestorpos(startraw, node)
        endpos = _ancestorpos(endraw, node)
        pos = startpos*startweight + endpos*endweight

        nodespos.append((node, pos))

    return Graph(nodespos,
                 radius=endgraph.radius, padding=endgraph.padding,
                 arrow_width=endgraph.arrow_width, arrow_length=endgraph.arrow_length)


def _ancestorpos(d, node):
    while node not in d:
        node = node.parent
    return d[node]


def _round(c, precision):
    return complex(round(c.real, precision), round(c.imag, precision))
