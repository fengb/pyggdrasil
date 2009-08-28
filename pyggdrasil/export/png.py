import cmath
import PIL.Image
import PIL.ImageDraw


SCALE = 8


def export(graph, filename):
    # Upscaling draw for anti-aliased downscale
    scaledgraph = graph.scale(SCALE)

    # I love inconsistent conventions
    image = PIL.Image.new('L', (int(scaledgraph.width), int(scaledgraph.height)),
                          '#FFFFFF')
    draw = PIL.ImageDraw.Draw(image)

    for node in scaledgraph:
        if scaledgraph.hasline(node):
            spos = scaledgraph.linestart(node)
            epos = scaledgraph.lineend(node)

            draw.line([spos.real, spos.imag, epos.real, epos.imag],
                      fill='#000000', width=SCALE)

            points = [(pos.real, pos.imag)
                          for pos in scaledgraph.arrowpoints(node)]
            draw.polygon(points, outline='#000000', fill='#000000')

    for node in scaledgraph:
        pos = scaledgraph.pos(node)

        # Draw concentric circles to emulate a wide brush
        for offset in range(SCALE):
            x1 = pos.real - scaledgraph.radius + offset
            y1 = pos.imag - scaledgraph.radius + offset
            x2 = pos.real + scaledgraph.radius - offset
            y2 = pos.imag + scaledgraph.radius - offset

            draw.ellipse((x1, y1, x2, y2),
                         outline='#000000', fill='#FFFFFF')

    image = image.resize((int(scaledgraph.width / SCALE), int(scaledgraph.height / SCALE)),
                         PIL.Image.ANTIALIAS)

    draw = PIL.ImageDraw.Draw(image)
    for node in graph:
        pos = graph.pos(node)

        w, h = draw.textsize(node.id)
        x = pos.real - int(w / 2)
        y = pos.imag - int(h / 2)
        draw.text((x, y), node.id)

    image.save(filename)
