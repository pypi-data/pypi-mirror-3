#/usr/bin/env python
'''
Created on Nov 13, 2011

@author: joseph
'''

from distutils.core import setup
from setuptools import find_packages

setup(name = "JsonRpcCmd",
      author = "Joseph Piron",
      author_email = "joseph.piron@gmail.com",
      version = "0.1",
      description = "Json RPC Command line utility",
      install_requires = ['jsonrpclib>=0.1.3'],
      zip_safe = True,
      scripts = ["src/jsonRpcCmd.py"])
