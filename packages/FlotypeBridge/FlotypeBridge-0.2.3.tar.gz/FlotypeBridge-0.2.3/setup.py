from distutils.core import setup

setup(
    name='FlotypeBridge',
    version='0.2.3',
    author='Flotype Inc.',
    author_email='team@flotype.com',
    packages=['flotype'],
    url='http://pypi.python.org/pypi/FlotypeBridge/',
    license='LICENSE.txt',
    description='A Python API for the Flotype Bridge service.',
    requires=[
        "tornado (>= 2.2)",
    ]
)
