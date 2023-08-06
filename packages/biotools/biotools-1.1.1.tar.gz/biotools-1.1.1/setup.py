#!/usr/bin/env python

from distutils.core import setup

setup(name="biotools",
      version='1.1.1',
      description="A bunch of bioinformatics utilities.",
      author="Andrew Kassen",
			maintainer="Andrew Kassen",
      author_email="atkassen@gmail.com",
			maintainer_email="atkassen@gmail.com",
			requires=['numpy','matplotlib'],
      packages=['biotools', 'biotools.analysis'],
			data_files=[('/usr/local/bin/', ['prok-geneseek'])],
			keywords=['gene prediction', 'prokaryotes', 'effectors'],
			classifiers=[
				'Development Status :: 5 - Production/Stable',
				'Intended Audience :: Science/Research',
				'License :: Free for non-commercial use',
				'Topic :: Scientific/Engineering :: Bio-Informatics'
			])
