try:
    # 2.5 built-in
    import xml.etree.ElementTree as et
except ImportError:
    # External library
    import elementtree.ElementTree as et


def export(graph, filename):
    root = et.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': str(graph.width), 'height': str(graph.height),
    })

    defs = et.SubElement(root, 'defs')
    # Base arrowhead is horizontal (looks like >)
    arrow = et.SubElement(defs, 'marker', {
        'id': 'arrowhead', 
        'viewBox': '0 0 %s %s' % (graph.arrowlength, graph.arrowwidth),
        'refX': str(graph.arrowlength), 'refY': str(graph.arrowwidth / 2.0),
        'markerUnits': 'strokeWidth',
        'markerWidth': str(graph.arrowlength), 'markerHeight': str(graph.arrowwidth),
        'orient': 'auto',
    })
    et.SubElement(arrow, 'polygon', {
        'points': '0,0 %s,%s 0,%s' % (graph.arrowlength, graph.arrowwidth / 2.0, graph.arrowwidth),
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

    file = open(filename, 'w')
    try:
        file.write(et.tostring(root))
    finally:
        file.close()
