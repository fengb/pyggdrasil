"""
Graph
    Standard graph interface that every algorithm should implement.

    Fields:
    base -- the base node used for graph generation
    width -- the width of the entire graph
    height -- the height of the entire graph

    Methods:
    __init__(self, base)
        base -- the base node

    __iter__(self) -> iterable
        Iterate through all the nodes in a fixed order (the same order as
        model.unroll).

    __getitem__(self, node) -> complex(x, y)
        Grab the position of the node.  Positions are represented as complex
        numbers for easy mathematical operations.
        real <=> x
        imag <=> y

        None is a possible return value, meaning do not draw.
"""
