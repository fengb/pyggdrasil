from pyggdrasil import model


class TestNode(object):
    def setup_method(self, method):
        self.node = model.Node(None)

    def test_assign_corresponding_child(self):
        child1 = model.Node(None, self.node)
        child2 = model.Node(None, self.node)
        assert child1.parent == self.node
        assert child2.parent == self.node
        assert child1 in self.node.children
        assert child2 in self.node.children


def test_unroll():
    node1 = model.Node(None)
    node11 = model.Node(None, node1)
    node12 = model.Node(None, node1)
    node13 = model.Node(None, node1)
    node131 = model.Node(None, node13)

    nodes = set(model.unroll(node1))

    assert node1 in nodes
    assert node11 in nodes
    assert node12 in nodes
    assert node13 in nodes
    assert node131 in nodes
    assert len(nodes) == 5
