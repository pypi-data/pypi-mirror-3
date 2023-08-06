#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "vizing",
    packages = ["vizing"],
    version = "0.0.11",
    description = "List-colouring of graphs",
    author = "Matthew Henderson",
    author_email = "matthew.james.henderson@gmail.com",
    url = "http://packages.python.org/vizing/",
    download_url = "http://pypi.python.org/pypi/vizing/",
    keywords = [""],
    classifiers = [
        "Programming Language :: Python",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
Vizing -- list-colouring of graphs in Python 
============================================

Vizing is a collection of Python code for working with list-colouring problems. List vertex-colourings and list edge-colourings are both of interest here. With Vizing you can easily build a variety of models of a list colouring problem instances and use solvers to find realisations of your models. 

Visualisations in LaTeX are provided via ``tkz-graph``."""
)
