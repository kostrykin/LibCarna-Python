#!/bin/bash
set -ex

# Create or update conda environment
export ROOT=$(dirname "$0")
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

# Build wheel
export CARNAPY_BUILD_TEST="OFF"
cd "$ROOT"
python setup.py bdist_wheel