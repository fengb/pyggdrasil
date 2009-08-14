

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
                packages='wx',
                site_packages=True,
            ),
        ),
    )
except:
    pass


setup(**args)
