import re
import yaml
import pyggdrasil


class NodeParseException(Exception): pass


def load(stream):
    raw = yaml.load(stream)
    return fromraw(raw)


def dump(stream, *args, **kwargs):
    raw = toraw(*args, **kwargs)
    yaml.dump(raw, stream=stream)


def toraw(root, options):
    ids = {}
    usedids = set()
    for node in root.unroll():
        id = node.id
        num = 0

        while id in usedids:
            id = '%s {{{%d}}}' % (node.id, num)
            num += 1

        ids[node] = id
        usedids.add(id)

    return {
        'data': dict((ids[node], node.data) for node in root.unroll()),
        'structure': _tostructure(root, ids),
        'options': options.dict,
    }

def _tostructure(node, ids):
    return {ids[node]: [_tostructure(child, ids) for child in node.children]}


def fromraw(raw):
    root = _fromstructure(raw['structure'], raw['data'])
    return root, pyggdrasil.model.Options(raw['options'])


def _fromstructure(structure, data, parent=None):
    if len(structure) != 1:
        raise NodeParseException()

    for (rawid, children) in structure.items():
        match = re.match(r'^(.*) \{\{\{\d*\}\}\}$', rawid)
        if match:
            id = match.group(1)
        else:
            id = rawid

        node = pyggdrasil.model.Node(id, data[rawid], parent)
        for child in children:
            childnode = _fromstructure(child, data, node)
        return node
