from distutils.core import setup

setup(
    name='msrflux',
    version='0.3',
    packages=['msrflux'],
    scripts=['bin/generate-nustorm-fd-flux.py', 'generate-nustorm-nd-flux.py'],
    url='http://pypi.python.org/pypi/msrflux/',
    license='LICENSE.txt',
    author='tunnell',
    author_email='c.tunnell1@physics.ox.ac.uk',
    description='Computes the neutrino flux from a muon decay ring while averaging over the detector and accelerator.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.6.0",
    ]
)
