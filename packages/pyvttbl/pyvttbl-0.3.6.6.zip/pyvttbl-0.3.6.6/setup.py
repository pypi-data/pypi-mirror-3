# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

##from distutils.core import setup
from setuptools import setup

setup(name='pyvttbl',
    version='0.3.6.6',
    description='Multidimensional pivot tables, data processing, statistical computation',
    author='Roger Lew',
    author_email='rogerlew@gmail.com',
    license = "BSD",
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Information Technology",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: BSD License",
                 "Natural Language :: English",
                 "Programming Language :: Python :: 2.5",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Database",
                 "Topic :: Database :: Database Engines/Servers",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 "Topic :: Scientific/Engineering :: Mathematics",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    url='http://code.google.com/p/pyvttbl/',
    packages=['pyvttbl',
              'pyvttbl.test',
              'pyvttbl.stats'])

"""setup.py sdist upload --identity="Roger Lew" --sign"""
