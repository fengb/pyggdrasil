

args = dict(
    name='Pyggdrasil',
    version='0.0.0',
    description='Pyggdrasil',
    packages=['pyggdrasil', 'pyggdrasil.graph'],
    scripts=['pygg'],
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


try:
    import py2app
    args.update(
        app=['pygg.pyw'],
        options=dict(
            py2app=dict(
                packages=['wx', 'yaml'],
                site_packages=True,
            ),
        ),
    )
except ImportError:
    pass


try:
    import py2exe
    args.update(
        windows=['pygg.pyw'],
        options=dict(
            py2exe=dict(
                dll_excludes=['MSVCP90.dll'],
            ),
        ),
    )
except ImportError:
    pass


setup(**args)
