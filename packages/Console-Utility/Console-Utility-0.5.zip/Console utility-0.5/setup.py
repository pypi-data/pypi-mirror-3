#!/usr/bin/env python

__author__ = "Alessandro Piccione"
__version__ = "0.5"
__date__ = '2011-09-18'

from distutils.core import setup

from alex75_console import menu
from alex75_console import selectors

setup(name='Console utility',
    version=__version__,
    description='Console utils for help on console programs',
    author=__author__,
    author_email='alessandro@alex75.it',
    #url='',
    #py_modules=[],
    #packages=['distutils','distutils.command'],      
    packages=['alex75_console'],  
    )
      