"""
Graph - any iterable with the following requirements:
    1. Each item must be a (node, position) pair.
    2. The first node must be the root.
    3. Every position is given as complex(x, y) to simplify calculations.
    4. A position may also be None, which means do not draw. A comparison
       should use "is None" since complex(0, 0) is a valid position.
    5. Every node is assumed to be size (1, 1).
"""


from . import topdown


def generate(root, algorithm=topdown):
    return NormalizedGraph(algorithm.generate(root))


class NormalizedGraph(object):
    """A Graph implementation with more functionality.
    Normalization calculates the minimum sized box (width, height) that can
    contain all of the nodes, taking into account the node size of (1, 1).

    Every node's position also shifts so that all of the nodes will be
    contained within the box (0, 0) and (width, height).

    Any Graph may be normalized. Normalizing a NormalizedGraph is possible and
    will not change any values but why would you waste CPU time like that?

    Fields:
        width
        height
    """
    def __init__(self, graph):
        cached = list(graph)

        xmin = min(pos.real for (node, pos) in cached) - 0.5
        xmax = max(pos.real for (node, pos) in cached) + 0.5
        ymin = min(pos.imag for (node, pos) in cached) - 0.5
        ymax = max(pos.imag for (node, pos) in cached) + 0.5

        self.width = xmax - xmin
        self.height = ymax - ymin

        offset = complex(xmin, ymin)
        self._graph = [(node, pos - offset) for (node, pos) in cached]

    def __iter__(self):
        return iter(self._graph)
