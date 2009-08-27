from . import svg


ALL = [svg]


def name(module):
    if hasattr(module, 'NAME'):
        return module.NAME
    else:
        return extension(module).upper()


def extension(module):
    if hasattr(module, 'EXTENSION'):
        return module.EXTENSION
    else:
        return module.__name__.rpartition('.')[2]
