# run python setup.py install to install
# run python setup.py sdist to generate a tarball

from distutils.core import setup

setup(

    name = 'libpgm',
    version = '1.1',
    author = 'Charles Cabot',
    author_email = 'cccabot@gmail.com',
    maintainer = 'Cyber Point International, LLC',
    maintainer_email = 'mraugas@cyberpointllc.com',
    url = 'http://pypi.python.org/pypi/libpgm',
    description = 'A library for creating and using probabilistic graphical models',
    long_description = 'This library provides tools for modeling large systems with Bayesian networks. Using these tools allows for efficient statistical analysis on large data sets using Bayesian Networks.',
    packages = ['libpgm', 'libpgm.CPDtypes'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Mathematics'
    ]
)
