from pyggdrasil import graph


THRESHOLD = 1e-8


def assert_floats(first, second):
    assert abs(first - second) < THRESHOLD


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

    def test_scale(self):
        value = 3.14
        scaled = self.graph.scale(value)

        assert_floats(scaled.width, self.graph.width * value)
        assert_floats(scaled.height, self.graph.height * value)
        assert_floats(scaled.radius, self.graph.radius * value)
        assert_floats(scaled.padding, self.graph.padding * value)
        for node in scaled:
            assert_floats(scaled.pos(node), self.graph.pos(node) * value)

