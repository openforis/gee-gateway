# gee-gateway

[![Python: 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a REST API designed to be used by [CEO (Collect Earth Online)](https://github.com/openforis/collect-earth-online) to interface with Google Earth Engine.

## REQUIREMENTS

1. [Python 2.7](https://www.python.org/)
2. [pip (package manager)](https://github.com/pypa/pip)
3. [Earth Engine Python API](https://developers.google.com/earth-engine/python_install)

## INSTALLATION

From project root directory

```bash
pip install -r requirements.txt
```

## CONFIGURATION

Edit the configuration file (config.py)

## EXECUTION

From project root directory

```bash
python run.py
```

## DOCUMENTATION

```bash
pip install sphinx
pip install sphinxcontrib-httpdomain
```

From project root directory

```bash
sphinx-build -aE -b html . static/docs
```

## STRUCTURE

    ├── README.md
    ├── license.txt
    ├── requirements.txt            third party libraries
    ├── config.py                   configuration file
    ├── run.py                      application start up
    ├── instance/                   (not in version control)
        ├── config.py               alternative configuration file (not in version control)
    ├── gee_gateway/                application folder
        ├── __init__.py             application initialization
        ├── utils.py
        ├── web/
             ├── __init__.py
             ├── errors.py          error handlers definition
             ├── routes.py          routes definition
        ├──  gee/
             ├── __init__.py
             ├── gee_exception.py
             ├── utils.py
    ├── conf.py                     sphinx (documentation) configuration file
    ├── index.rst                   sphinx index file
    ├── static/                     static resources folder
             ├── index.html         playground
             ├── assets/            css, images, js, libs and fonts
             ├── docs/              documentation folder
                  ├── index.html