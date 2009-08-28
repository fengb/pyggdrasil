import PIL.Image
import PIL.ImageDraw


SCALE = 8


def export(graph, filename):
    # Upscaling draw for anti-aliased downscale
    graph = graph.scale(SCALE)

    # I love inconsistent conventions
    image = PIL.Image.new('L', (int(graph.width), int(graph.height)), '#FFFFFF')
    draw = PIL.ImageDraw.Draw(image)

    for node in graph:
        if graph.hasline(node):
            spos = graph.linestart(node)
            epos = graph.lineend(node)

            draw.line([spos.real, spos.imag, epos.real, epos.imag],
                      fill='#000000', width=SCALE)

    image = image.resize((int(graph.width / SCALE), int(graph.height / SCALE)),
                         PIL.Image.ANTIALIAS)
    image.save(filename)
