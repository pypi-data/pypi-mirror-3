#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
import src.__init__ as src

setup(
    name = 'neuronpy',
    version = src.__version__,
    package_dir = {'neuronpy': 'src'},
    packages = ['neuronpy',
                'neuronpy.graphics',
                'neuronpy.math',
                'neuronpy.nrnobjects',
                'neuronpy.util'],
    url = src.__url__,
    license = src.__license__,
    author = src.__author__,
    author_email = src.__email__,
    description = 'Python interfaces and utilities for interacting with the NEURON simulator and analyzing neural data.',
    long_description = src.__doc__,
    keywords = 'neuron neural simulation simulator raster',
    platforms = 'any',
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Environment :: Web Environment',
                   'Intended Audience :: Science/Research',
                   'License :: Other/Proprietary License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering'],
    #requires = ['NEURON Simulation Environment ( >= 7.1 )', 'matplotlib', 'numpy'],
)
