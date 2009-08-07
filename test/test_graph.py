import random
from pyggdrasil import graph


class TestNormalizedGraph(object):
    def setup_method(self, method):
        self.xmin = -28.0
        self.ymin = -925.0
        self.xmax = 479.0
        self.ymax = 308.0
        self.original = [
            ('root', complex(self.xmin, self.ymin)),
            ('peak', complex(self.xmax, self.ymax)),
        ]

        self.graph = graph.NormalizedGraph(self.original)

    def test_dimensions(self):
        assert self.graph.width == self.xmax - self.xmin + 1
        assert self.graph.height == self.ymax - self.ymin + 1

    def test_positions(self):
        for (node, pos) in self.graph:
            assert 0.5 <= pos.real <= self.graph.width - 0.5
            assert 0.5 <= pos.imag <= self.graph.height - 0.5