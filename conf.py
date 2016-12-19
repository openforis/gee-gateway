# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinxcontrib.httpdomain',
    'sphinxcontrib.autohttp.flask',
    'sphinxcontrib.autohttp.flaskqref',
]

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'gee-gateway'
copyright = u'2016, Open Foris'
author = u'Roberto Fontanarosa'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['docs/_build', 'Thumbs.db', '.DS_Store']
