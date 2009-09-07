from distutils.core import setup


args = dict(
    name='Pyggdrasil',
    version='0.0.3',
    description='Pyggdrasil',
    packages=['pyggdrasil', 'pyggdrasil.graph', 'pyggdrasil.export'],
    scripts=['pygg'],
)


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
