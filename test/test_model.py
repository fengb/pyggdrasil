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

    def test_remove_corresponding_child(self):
        child1 = model.Node(None, self.node)
        child2 = model.Node(None, self.node)
        child1.parent = None
        child2.parent = None
        assert len(self.node.children) == 0


def test_unroll_in_order_of_node_then_children_then_descendents():
    # TODO: Less hardcode, more awesome code
    node1 = model.Node(None)
    node11 = model.Node(None, node1)
    node12 = model.Node(None, node1)
    node13 = model.Node(None, node1)
    node111 = model.Node(None, node11)
    node131 = model.Node(None, node13)
    node1311 = model.Node(None, node13)

    nodes = list(model.unroll(node1))

    assert nodes[0] == node1
    assert nodes[1] == node11
    assert nodes[2] == node12
    assert nodes[3] == node13
    assert nodes[4] == node111
    assert nodes[5] == node131
    assert nodes[6] == node1311
    assert len(nodes) == 7
