project = 'libcarna-python'
copyright = '2021-2025 Leonid Kostrykin'
author = 'Leonid Kostrykin'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'nbsphinx',
]

html_logo = 'logo.png'
html_static_path = ['_static']
html_css_files = ['custom.css']

import os
import sys

LIBCARNA_PYTHON_PATH = os.environ.get('LIBCARNA_PYTHON_PATH')
sys.path.append(LIBCARNA_PYTHON_PATH)
os.environ['PYTHONPATH'] = LIBCARNA_PYTHON_PATH + ':' + os.environ.get('PYTHONPATH', '')
print('*** LIBCARNA_PYTHON_PATH:', LIBCARNA_PYTHON_PATH)
#LIBCARNA_PYTHON_PATH = os.path.abspath(os.environ.get('LIBCARNA_PYTHON_PATH'))
#sys.path.append(LIBCARNA_PYTHON_PATH)
#os.environ['PYTHONPATH'] = LIBCARNA_PYTHON_PATH + ':' + os.environ.get('PYTHONPATH', '')

nbsphinx_execute = 'always'