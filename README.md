# gee-gateway

[![Python: 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A REST API designed to be used by [CEO (Collect Earth Online)](https://github.com/openforis/collect-earth-online) to interface with Google Earth Engine.

## REQUIREMENTS

1. [Python 3.7](https://www.python.org/)
2. [pip (package manager)](https://github.com/pypa/pip)
3. [Earth Engine Python API](https://developers.google.com/earth-engine/python_install)
4. [virtualenv](https://pypi.python.org/pypi/virtualenv) (Optional)

## INSTALLATION

From project root directory

```bash
sudo pacman -S uwsgi uwsgi-plugin-python nginx
pip install -r requirements.txt
```

OR using **virtualenv** (Optional)

```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## CONFIGURATION

Edit the configuration file (`config.py` or `instance/config.py`)


```code
create /etc/uwsgi/vassals/gee-gateway.ini (template found in nginx directory)
create /etc/nginx/nginx.config {path to gateway instance}
```

## EXECUTION

From project root directory

```bash
sudo systemctl enable nginx emperor.uwsgi
sudo systemctl start nginx emperor.uwsgi
```

Note: to stop

```bash
sudo systemctl stop nginx emperor.uwsgi
```

OR using **virtualenv** (Optional)

```bash
source env/bin/activate
sudo systemctl enable nginx emperor.uwsgi
sudo systemctl start nginx emperor.uwsgi
```

```bash
usage: run.py [-h] [--gmaps_api_key GMAPS_API_KEY] [--ee_account EE_ACCOUNT]
              [--ee_key_path EE_KEY_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --gmaps_api_key GMAPS_API_KEY
                        Google Maps API key
  --ee_account EE_ACCOUNT
                        Google Earth Engine account
  --ee_key_path EE_KEY_PATH
                        Google Earth Engine key path
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
    ├── requirements.txt            list of third party packages to install
    ├── routes.py                      application start up and routing
    ├── instance/                   (not in version control)
	├── config.py               alternative configuration file (not in version control)

	├── __init__.py             blueprint initialization
	├── gee/
		├── __init__.py
		├── gee_exception.py
		├── utils.py
	├── templates/              blueprint templates
		├── index.html          playground
	├── static/                 blueprint static files
		├── assets/             css, images, js, libs and fonts
    ├── conf.py                     sphinx (documentation) configuration file
    ├── index.rst                   sphinx index file
    ├── static/                     static resources folder
        ├── docs/                   documentation folder
            ├── index.html