#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup

import sys
from rst2slides import __version__


long_description = open('README.rst').read()


setup(
    name = 'rst2slides',
    version = __version__,
    description = 'Generates an HTML5 slideshow document from standalone '
                  'reStructuredText sources.',
    long_description = long_description, 
    author = u'Martín Gaitán'.encode('UTF-8'),
    author_email = 'gaitan@gmail.com',
    url='https://bitbucket.org/tin_nqn/rst2slides',
    packages = ['rst2slides'],
    package_data={'rst2slides': ['data/**/*.*']},

    license = 'GNU GENERAL PUBLIC LICENCE v3.0',
    scripts = ['bin/rst2slides'],
    install_requires = ['docutils>=0.7', 'pygments','roman'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup',
      ],

)
