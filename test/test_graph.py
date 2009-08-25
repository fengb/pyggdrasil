from pyggdrasil import graph


class TestGraph(object):
    def setup_method(self, method):
        self.xmin = -28.0
        self.ymin = -925.0
        self.xmax = 479.0
        self.ymax = 308.0
        self.rawgraph = [
            ('root', complex(self.xmin, self.ymin)),
            ('peak', complex(self.xmax, self.ymax)),
        ]

        self.graph = graph.Graph(self.rawgraph)
        self.unnormalized = graph.Graph(self.rawgraph, normalize=False)

    def test_dimensions(self):
        assert self.graph.width == self.xmax - self.xmin + 1
        assert self.graph.height == self.ymax - self.ymin + 1

    def test_positions(self):
        for node in self.graph:
            pos = self.graph.pos(node)
            assert 0.5 <= pos.real <= self.graph.width - 0.5
            assert 0.5 <= pos.imag <= self.graph.height - 0.5

    def test_unnormalized_dimensions_same_as_graph(self):
        assert self.unnormalized.width == self.graph.width
        assert self.unnormalized.height == self.graph.height

    def test_unnormalized_positions_same_as_rawgraph(self):
        basepos = dict(self.rawgraph)
        for node in self.unnormalized:
            assert self.unnormalized.pos(node) == basepos[node]

    def test_unscaled_unnormalized_positions_same_as_target(self):
        target = graph.Graph(self.graph.raw(), scale=False, normalize=False,
                             radius=281, padding=48)
        for node in target:
            assert target.pos(node) == self.graph.pos(node)

