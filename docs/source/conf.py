# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'amad'
copyright = '2024, AKKODIS'
author = 'Andre Hochschulz'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.duration",
    "sphinx.ext.autosectionlabel",
    "nbsphinx",
    "nbsphinx_link",
    "sphinx.ext.autodoc",
    'sphinx.ext.autosummary',
    'autoapi.extension'
]

templates_path = ['_templates']
exclude_patterns = []
autoapi_dirs = ['../..']
autoapi_ignore = ["*/conf.py", "*/test_*.py"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster', 'furo'
# html_theme = 'furo'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
