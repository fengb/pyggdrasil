"""
Graph
    Standard graph interface that every algorithm should implement.

    Fields
    ---
    radius - the preconfigured node radius used for generation
    width - the width of the entire graph
    height - the height of the entire graph

    Methods
    ---
    __init__(self, base, radius)
        base - the base node
        radius - the radius to use for each node

    __iter__(self) -> Node
        Iterate through all the nodes.

    __getitem__(self, node) -> (x, y)
        Grab the position of the node.
"""
