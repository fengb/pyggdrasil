import pyggdrasil


def assert_equal_nodes(node1, node2):
    assert node1.id == node2.id
    assert node1.data == node2.data
    for (child1, child2) in zip(node1.children, node2.children):
        assert_equal_nodes(child1, child2)


class TestNode(object):
    def setup_method(self, method):
        # TODO: Move node data elsewhere
        self.root = pyggdrasil.model.Node('the root', 'test data')
        self.child1 = pyggdrasil.model.Node('child uno', 'some test', self.root)
        self.child2 = pyggdrasil.model.Node('child duo', 'uber test', self.root)
        self.grandchild1 = pyggdrasil.model.Node('child fool', 'uber test', self.child1)
        self.graphoptions = {1: 'a', 2: 'b', 3: 'c'}

    def test_convert_to_and_from_raw(self):
        raw = pyggdrasil.serialize.toraw(self.root, self.graphoptions)
        root, graphoptions = pyggdrasil.serialize.fromraw(raw)

        assert_equal_nodes(root, self.root)
        assert graphoptions == self.graphoptions
