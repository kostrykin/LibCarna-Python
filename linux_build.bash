#!/bin/bash
set -ex

# Create or update conda environment
export ROOT="$PWD"/$(dirname "$0")
if [ ! -d "$ROOT/.env" ]; then
    conda env create -f "$ROOT/environment.yml" --prefix "$ROOT/.env"
else
    conda env update -f "$ROOT/environment.yml" --prefix "$ROOT/.env" --prune
fi

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate "$ROOT/.env"

# Setup and check dependencies
export PYBIND11_PREFIX="$CONDA_PREFIX/share/cmake/pybind11"
export CMAKE_MODULE_PATH="$CONDA_PREFIX/share/cmake/Modules"

# Default to not building the test suite
if [ -z "$LIBCARNA_PYTHON_BUILD_TEST" ]; then
    export LIBCARNA_PYTHON_BUILD_TEST="OFF"
fi

# Build wheel and test
cd "$ROOT"
python setup.py bdist_wheel

# Optionally, build the documentation
if [ -v LIBCARNA_PYTHON_BUILD_DOCS ]; then
    pip install -r docs/requirements.txt
    export LIBCARNA_PYTHON_PATH="$ROOT/build/make_release"
    rm -rf $ROOT/docs/build
    sphinx-build -M html docs docs/build
    cp $ROOT/docs/build/html/examples/*.ipynb $ROOT/examples/
fi