#!/usr/bin/env python

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

def getVersion():
    return '1.0'

def getInstallRequires():
    requirements = []
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements

setup(
    name='gee-gateway',
    version=getVersion(),
    description='Google Earth Engine Gateway',
    author='Roberto Fontanarosa',
    author_email='roberto.fontanarosa@fao.org',
    url='https://github.com/openforis/gee-gateway',
    packages=['gee_gateway', 'gee_gateway.gee', 'gee_gateway.web'],
    include_package_data=True,
    install_requires=getInstallRequires()
)