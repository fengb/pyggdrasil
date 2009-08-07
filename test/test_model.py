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

    def test_unroll_in_order_of_node_then_children_then_descendents(self):
        # TODO: Less hardcode, more awesome code
        nodes = list(self.root.unroll())

        assert nodes[0] == self.root
        assert nodes[1] == self.child1
        assert nodes[2] == self.child2
        assert nodes[3] == self.grandchild1
        assert len(nodes) == 4

    def assert_equal(self, node1, node2):
        assert node1.id == node2.id
        assert node1.data == node2.data
        for (child1, child2) in zip(node1.children, node2.children):
            self.assert_equal(child1, child2)

