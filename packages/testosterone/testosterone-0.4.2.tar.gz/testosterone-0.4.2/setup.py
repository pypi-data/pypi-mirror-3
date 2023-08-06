#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


classifiers = [
    'Development Status :: 4 - Beta'
  , 'Environment :: Console'
  , 'Environment :: Console :: Curses'
  , 'Intended Audience :: Developers'
  , 'License :: Freeware'
  , 'Natural Language :: English'
  , 'Operating System :: MacOS :: MacOS X'
  , 'Operating System :: Microsoft :: Windows'
  , 'Operating System :: POSIX'
  , 'Programming Language :: Python'
  , 'Topic :: Software Development :: Testing'
                ]

setup( name = 'testosterone'
     , version = '0.4.2'
     , packages = [ 'testosterone'
                  , 'testosterone.cli'
                  , 'testosterone.interactive'
                  , 'testosterone.interactive.screens'
                  , 'testosterone.tests'
                  , 'testosterone.tests.interactive'
                   ]
     , entry_points = { 'console_scripts'
                      : [ 'testosterone = testosterone.cli.main:main' ]
                       }
     , description = 'testosterone is a manly testing interface for Python.'
     , author = 'Chad Whitacre'
     , author_email = 'chad@zetaweb.com'
     , url = 'http://www.zetadev.com/software/testosterone/'
     , classifiers = classifiers
      )
