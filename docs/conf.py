project = 'libcarna-python'
copyright = '2021-2025 Leonid Kostrykin'
author = 'Leonid Kostrykin'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]

html_logo = 'logo.png'
html_static_path = ['_static']
html_css_files = ['custom.css']

import os
import sys

sys.path.append(os.environ['LIBCARNA_PYTHON_PATH'])