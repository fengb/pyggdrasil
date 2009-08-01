from pyggdrasil import model


class TestNode(object):
    def setup_method(self, method):
        self.root = model.Node('the root', 'test data')
        self.child1 = model.Node('child uno', 'some test', self.root)
        self.child2 = model.Node('child duo', 'uber test', self.root)
        self.grandchild1 = model.Node('child fool', 'uber test', self.child1)

    def test_assign_corresponding_child(self):
        assert self.child1.parent == self.root
        assert self.child2.parent == self.root
        assert self.child1 in self.root.children
        assert self.child2 in self.root.children

    def test_remove_corresponding_child(self):
        self.child1.parent = None
        self.child2.parent = None
        assert len(self.root.children) == 0

    def test_convert_to_and_from_raw(self):
        raw = self.root.raw()
        generated = model.Node.from_raw(raw)

        self.assert_equal(generated, self.root)

    def assert_equal(self, node1, node2):
        assert node1.id == node2.id
        assert node1.data == node2.data
        for (child1, child2) in zip(node1.children, node2.children):
            self.assert_equal(child1, child2)


"""
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
"""
