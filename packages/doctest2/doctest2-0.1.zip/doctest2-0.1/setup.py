#!/usr/bin/env python
from distutils.core import setup

TROVE_CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Unix Shell",
    "Topic :: Documentation",
    "Topic :: Software Development",
    "Topic :: Software Development :: Testing",
]

setup(name='doctest2',
      version='0.1',
      description='Enhanced doctest library',
      author='Devin Jeanpierre (and the original authors of doctest)',
      author_email='jeanpierreda@gmail.com',
      packages=[
          'doctest2',
          'doctest2.scripts',
          'doctest2.tests',
          'doctest2.languages'],
      url='https://bitbucket.org/devin.jeanpierre/doctest2/',
      classifiers=TROVE_CLASSIFIERS,
      license='MIT'
     )
