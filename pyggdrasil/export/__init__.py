ALL = []


try:
    import svg
    ALL.append((svg, True))
except ImportError:
    ALL.append(('svg', False))

try:
    import png
    ALL.append((png, True))
except ImportError:
    ALL.append(('png', False))


def run(module, graph, filename, progresscallback=None):
    if not progresscallback:
        def updatefunc(value):
            pass
    module.export(graph, filename, progresscallback)


def name(module):
    if hasattr(module, 'NAME'):
        return module.NAME
    else:
        return extension(module).upper()


def extension(module):
    if hasattr(module, 'EXTENSION'):
        return module.EXTENSION
    elif hasattr(module, '__name__'):
        return module.__name__.rpartition('.')[2]
    else:
        return str(module)
