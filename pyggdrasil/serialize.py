import yaml
import pyggdrasil


class NodeParseException(Exception): pass


def load(stream):
    raw = yaml.load(stream)
    return fromraw(raw)


def dump(stream, *args, **kwargs):
    raw = toraw(*args, **kwargs)
    yaml.dump(raw, stream=stream)


def toraw(root, graphoptions):
    return {
        'data': dict((node.id, node.data) for node in root.unroll()),
        'structure': _tostructure(root),
        'graph': graphoptions,
    }

def _tostructure(self):
    return {self.id: [_tostructure(child) for child in self.children]}


def fromraw(raw):
    return _fromstructure(raw['structure'], raw['data']), raw['graph']


def _fromstructure(structure, data, parent=None):
    if len(structure) != 1:
        raise NodeParseException()

    for (id, children) in structure.items():
        node = pyggdrasil.model.Node(id, data[id], parent)
        for child in children:
            child_id = _fromstructure(child, data, node)
        return node
