#!/bin/bash
set -ex

# Create or update conda environment
export ROOT="$PWD"/$(dirname "$0")
if [ ! -d "$ROOT"/.env ]; then
    conda env create -f "$ROOT"/environment.yml --prefix "$ROOT"/.env
else
    conda env update -f "$ROOT"/environment.yml --prefix "$ROOT"/.env --prune
fi

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate "$ROOT"/.env

# Create build directory
mkdir -p "$ROOT"/build

# Build native extension
cd "$ROOT"/build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DPYTHON_EXECUTABLE="$(which python)" \
      -Dpybind11_DIR="$CONDA_PREFIX/share/cmake/pybind11" \
      -DCMAKE_MODULE_PATH="$CONDA_PREFIX/share/cmake/Modules" \
      "$ROOT"
make VERBOSE=1

# Build wheel
python -m build --no-isolation

# Install wheel
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --no-deps dist/*.whl

# Optionally, run the test suite
if [ -v LIBCARNA_PYTHON_BUILD_TEST ]; then
    cd "$ROOT"
    pip install -r test/requirements.txt
    python -m unittest
fi

# Optionally, build the documentation
if [ -v LIBCARNA_PYTHON_BUILD_DOCS ]; then
    cd "$ROOT"
    pip install -r docs/requirements.txt
    rm -rf docs/build
    sphinx-build -M html docs docs/build
    cp docs/build/html/examples/*.ipynb /examples/
fi