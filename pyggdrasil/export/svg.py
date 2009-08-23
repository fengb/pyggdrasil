import cmath


try:
    # 2.5 built-in
    import xml.etree.ElementTree as et
except ImportError:
    # External library
    import elementtree.ElementTree as et


def export(graph):
    root = et.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': str(graph.width), 'height': str(graph.height),
    })

    defs = et.SubElement(root, 'defs')
    arrowwidth, arrowheight = _arrowdimensions(graph)
    # X and Y are reversed
    arrow = et.SubElement(defs, 'marker', {
        'id': 'arrowhead', 
        'viewBox': '0 0 %s %s' % (arrowheight, arrowwidth),
        'refX': str(arrowheight), 'refY': str(arrowwidth / 2.0),
        'markerUnits': 'strokeWidth',
        'markerWidth': str(arrowheight), 'markerHeight': str(arrowwidth),
        'orient': 'auto',
    })
    et.SubElement(arrow, 'polygon', {
        'points': '0,0 %s,%s 0,%s' % (arrowheight, arrowwidth / 2.0, arrowwidth),
        'fill': 'black', 'stroke': 'black',
    })

    for node in graph:
        if graph.hasline(node):
            spos = graph.linestart(node)
            epos = graph.lineend(node)
            et.SubElement(root, 'line', {
                'x1': str(spos.real), 'y1': str(spos.imag),
                'x2': str(epos.real), 'y2': str(epos.imag),
                'stroke': 'black',
                'marker-end': 'url(#%s)' % arrow.get('id'),
            })

    for node in graph:
        pos = graph.pos(node)

        group = et.SubElement(root, 'g')

        et.SubElement(group, 'circle', {
            'cx': str(pos.real), 'cy': str(pos.imag), 'r': str(graph.radius),
            'stroke': 'black', 'fill': 'white',
        })
        text = et.SubElement(group, 'text', {
            'x': str(pos.real), 'y': str(pos.imag),
            'text-anchor': 'middle', 'alignment-baseline': 'mathematical',
        })
        text.text = node.id

    return et.tostring(root)


def _arrowdimensions(graph):
    vector = graph.arrowlength * cmath.exp((cmath.pi / 2.0 - graph.arrowwidth / 2.0) * 1j)
    return 2.0 * vector.real, vector.imag
