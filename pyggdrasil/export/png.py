import PIL.Image
import PIL.ImageDraw


SCALE = 4.0


def export(graph, filename):
    # I love inconsistent conventions
    image = PIL.Image.new('RGBA', (int(graph.width), int(graph.height)), '#FFFFFF')
    draw = PIL.ImageDraw.Draw(image)

    for node in graph:
        if graph.hasline(node):
            spos = graph.linestart(node)
            epos = graph.lineend(node)

            draw.line([spos.real, spos.imag, epos.real, epos.imag], fill='#000000')

    image.save(filename)
