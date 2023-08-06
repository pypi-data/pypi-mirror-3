#!/usr/bin/env python

from distutils.core import setup

setup(name="biotools",
      version='1.0',
      description="A bunch of bioinformatics utilities.",
      author="sonwell",
      author_email="atkassen@gmail.com",
      packages=['biotools', 'biotools.analysis'],
			data_files=[('/usr/local/bin/', ['prok-geneseek'])])
