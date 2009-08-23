import py
import pyggdrasil


class TestNode(object):
    def setup_method(self, method):
        self.root = pyggdrasil.model.Node('the root', 'test data')
        self.child1 = pyggdrasil.model.Node('child uno', 'some test', self.root)
        self.child2 = pyggdrasil.model.Node('child duo', 'uber test', self.root)
        self.grandchild1 = pyggdrasil.model.Node('child fool', 'uber test', self.child1)

    def test_assign_corresponding_child(self):
        assert self.child1.parent == self.root
        assert self.child2.parent == self.root
        assert self.child1 in self.root.children
        assert self.child2 in self.root.children

    def test_remove_corresponding_child(self):
        self.child1.parent = None
        self.child2.parent = None
        assert len(self.root.children) == 0

    def test_unroll_in_order_of_node_then_children_then_descendents(self):
        # TODO: Less hardcode, more awesome code
        nodes = list(self.root.unroll())

        assert nodes[0] == self.root
        assert nodes[1] == self.child1
        assert nodes[2] == self.child2
        assert nodes[3] == self.grandchild1
        assert len(nodes) == 4

    def test_hasancestor(self):
        assert self.grandchild1.hasancestor(self.child1)
        assert self.grandchild1.hasancestor(self.root)
        assert not self.grandchild1.hasancestor(self.child2)

    def test_reject_circular_tree(self):
        py.test.raises(pyggdrasil.model.CircularTreeException,
                       'self.root.parent = self.grandchild1')

