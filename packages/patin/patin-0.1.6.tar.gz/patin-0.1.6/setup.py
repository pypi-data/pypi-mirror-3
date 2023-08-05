#!/usr/bin/env python
import sys
from setuptools import setup
from setuptools import find_packages
from patin import patin_version

setup(
        name='patin',
        version=patin_version.VERSION,
        description='Simple develop kit for kids and programming teachers.',
        author='Hugo Ruscitti',
        author_email='hugoruscitti@gmail.com',
        url='http://www.patin.ep.io',
        install_requires=[
            'setuptools',
            ],
        packages=['patin', 'patin.ui', 'patin.simplegui', 'patin.simplegui.console', 'patin.documentacion'],
        include_package_data = True,
        package_data = {
           'ui': ['patin/ui/*'],
           'documentacion': ['patin/documentacion/*'],
            },

        scripts=['bin/patin'],

        classifiers = [
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Natural Language :: Spanish',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Games/Entertainment',
            'Topic :: Education',
            'Topic :: Software Development :: Libraries',
          ],
    )

