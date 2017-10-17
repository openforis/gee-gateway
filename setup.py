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
    install_requires=[
        "Flask>=0.12.2",
        "Flask-Cors==3.0.3",
        "google-api-python-client>=1.6.2",
        "pyCrypto>=2.6.1"
    ],
    dependency_links=[
        "git+git://github.com/openforis/earthengine-api.git@v0.1.124.1#egg=earthengine-api&subdirectory=python"
    ]
)