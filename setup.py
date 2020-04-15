#!/usr/bin/env python

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

def getVersion():
    return '1.1.1'

def getInstallRequires():
    requirements = []
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements

setup(
    name='gee-gateway',
    version=getVersion(),
    description='A REST API designed to be used by CEO (Collect Earth Online) to interface with Google Earth Engine.',
    author='Roberto Fontanarosa',
    author_email='roberto.fontanarosa@fao.org',
    url='https://github.com/openforis/gee-gateway',
    packages=['gee_gateway', 'gee_gateway.gee', 'gee_gateway.web'],
    include_package_data=True,
    install_requires=[
        'Flask>=1.1.2',
        'Flask-Cors>=3.0.8',
        'google-api-python-client>=1.8.0',
        'pyCrypto>=2.6.1',
        'numpy>=1.18.2',
        'oauth2client>=4.1.3'
    ],
    dependency_links=[
        'git+git://github.com/openforis/earthengine-api.git@v0.1.217#egg=earthengine-api&subdirectory=python'
    ]
)