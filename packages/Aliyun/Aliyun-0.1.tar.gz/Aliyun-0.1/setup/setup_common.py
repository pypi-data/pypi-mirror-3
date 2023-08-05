# -*- coding: utf-8 -
from ConfigParser import SafeConfigParser
from setuptools import find_packages, Extension
from os import path

def get_metadata():
    config = SafeConfigParser()
    config.read(['metadata.cfg'])

    metadata = dict(config.items('metadata'))

    #metadata['py_modules'] = filter(None, metadata['py_modules'].split('\n'))
    metadata['classifiers'] = filter(None, metadata['classifiers'].split('\n'))
    metadata['scripts'] = filter(None, metadata['scripts'].split('\n'))
    metadata['install_requires'] = filter(None, metadata['install_requires'].split('\n'))
    metadata['package_dir'] = {'': 'src'}
    metadata['packages'] = find_packages(path.abspath(path.normpath(path.dirname(__file__) + '/../src')))
    metadata['ext_modules'] = [Extension('_aliyun', sources=['src/_aliyun.c'])]

    return metadata
