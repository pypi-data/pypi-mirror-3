try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup, find_packages

import sys, os

sys.path.insert(0,'lib')

setup(
    name         = 'simplemapplot',
    version      = '1.0.1',
    description  = "Simple functions for coloring maps",
    long_description = open('README.txt').read(),
    author       = 'Michael Anderson',
    author_email = 'mbanderson@uwalumni.com',
    url          = 'http://pypi.python.org/pypi/simplemapplot/',
    install_requires = ['BeautifulSoup'],
    packages = ['simplemapplot'],
    classifiers  = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
        ],
    )
