class Graph(object):
    def __init__(self, base, radius):
        self.base = base
        self.radius = radius

        self._subgraph_breadths = {}
        self._subgraph_depths = {}

    @property
    def width(self):
        return self.subgraph_breadth(self.base) * self.radius * 2

    @property
    def height(self):
        return self.subgraph_depth(self.base) * self.radius * 2

    def __iter__(self):
        pass

    def __getitem__(self, node):
        pass

    def subgraph_breadth(self, node):
        if node not in self._subgraph_breadths:
            if children:
                self._subgraph_breadths[node] = sum(self.subgraph_breadth(child)
                                                  for child in node.children)
            else:
                self._subgraph_breadths[node] = 1
        return self._subgraph_breadths[node]

    def subgraph_depth(self, node):
        if node not in self._subgraph_depths:
            if children:
                self._subgraph_depths[node] = 1 + max(self.node_height(child)
                                                       for child in node.children)
            else:
                self._subgraph_depths[node] = 1
        return self._subgraph_depths[node]
