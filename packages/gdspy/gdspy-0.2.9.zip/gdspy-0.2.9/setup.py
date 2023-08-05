#!/usr/bin/env python

########################################################################
##                                                                    ##
##  Copyright 2009-2011 Lucas Heitzmann Gabrielli                     ##
##                                                                    ##
##  This file is part of gdspy.                                       ##
##                                                                    ##
##  gdspy is free software: you can redistribute it and/or modify it  ##
##  under the terms of the GNU General Public License as published    ##
##  by the Free Software Foundation, either version 3 of the          ##
##  License, or any later version.                                    ##
##                                                                    ##
##  gdspy is distributed in the hope that it will be useful, but      ##
##  WITHOUT ANY WARRANTY; without even the implied warranty of        ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     ##
##  GNU General Public License for more details.                      ##
##                                                                    ##
##  You should have received a copy of the GNU General Public         ##
##  License along with gdspy.  If not, see                            ##
##  <http://www.gnu.org/licenses/>.                                   ##
##                                                                    ##
########################################################################

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

from distutils.core import setup, Extension

setup(name='gdspy',
      version='0.2.9',
      author='Lucas Heitzmann Gabrielli',
      author_email='heitzmann@gmail.com',
      license='GNU General Public License (GPL)',
      url='https://sourceforge.net/projects/gdspy/',
      description='A Python GDSII exporter',
      long_description='Module for creating GDSII stream files. It also allows the geometry created to be visualized.',
      packages = ['gdspy'],
      package_dir = {'gdspy': 'src'},
      ext_modules = [Extension('gdspy.boolext', ['src/boolext.c'])],
      zip_safe = True,
      provides=['gdspy'],
      requires=['numpy'],
      platforms='OS Independent',
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering'],
      cmdclass={'build_py': build_py})
