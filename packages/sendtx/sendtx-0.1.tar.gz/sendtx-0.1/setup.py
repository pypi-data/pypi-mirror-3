#!/usr/bin/env python
#from distribute_setup import use_setuptools
#use_setuptools()

from distutils.core import setup

setup(name='sendtx',
      version='0.1',
      description='Send serialized bitcoin transaction from commandline to selected bitcoin node',
      author='slush',
      author_email='info@bitcion.cz',
      packages=['sendtx',],
      requires=['twisted',],
      scripts=['scripts/sendtx',],
     )
