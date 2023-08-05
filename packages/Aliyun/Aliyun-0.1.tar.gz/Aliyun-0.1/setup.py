#!/usr/bin/env python
# -*- coding: utf-8 -

# For those whom don't have setuptools 
import ez_setup
ez_setup.use_setuptools()

# Main setup.py script
from setuptools import setup
from os import name 

if name == 'posix':
    from setup.setup_posix import get_config
else: # windows
    from setup.setup_windows import get_config

metadata = get_config()
import pprint
pprint.pprint(metadata)
setup(**metadata)
