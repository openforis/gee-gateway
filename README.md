# gee-gateway

This is a REST API designed to be used by [CEO (Collect Earth Online)](https://github.com/openforis/collect-earth-online) to interface with Google Earth Engine.

## INSTALLATION

### Google Earth Engine

> https://developers.google.com/earth-engine/python_install

### gee-gateway

From project root directory

> pip install -r requirements.txt

## INSTALLATION

> python run.py

From project root directory

## STRUCTURE

    ├── README.md
    ├── license.txt
    ├── requirements.txt            third party libraries
    ├── config.py                   configuration file
    ├── run.py                      application start up
    ├── instance                    (not in version control)
       ├── config.py                alternative configuration file
    ├── gee_gateway                 application folder
       ├── __init__.py              application initialization
       ├── utils.py
       ├── api
       │   ├── __init__.py
       │   ├── routes.py             routes definition
       │   ├── errors.py             error handlers definition
       ├── gee
       │   ├── __init__.py
       │   ├── utils.py