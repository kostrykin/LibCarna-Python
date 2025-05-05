#!/bin/bash

export LIBCARNA_PYTHON_VERSION=`python - << END
import yaml
with open('VERSIONS.yaml', 'r') as io:
    versions = yaml.safe_load(io)
print(versions['build']['carnapy'])
END`

cd ..
python setup.py sdist
python -m twine upload dist/LibCarnaPy-$LIBCARNA_PYTHON_VERSION.tar.gz

