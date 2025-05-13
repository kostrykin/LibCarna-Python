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

# Build native extension
mkdir -p "$ROOT"/build
cd "$ROOT"/build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DPYTHON_EXECUTABLE="$(which python)" \
      -Dpybind11_DIR="$CONDA_PREFIX/share/cmake/pybind11" \
      -DCMAKE_MODULE_PATH="$CONDA_PREFIX/share/cmake/Modules" \
      "$ROOT"
make VERBOSE=1

# Build wheel
python -m build --no-isolation

# Optionally, run the test suite
if [ -v LIBCARNA_PYTHON_BUILD_TES ]; then
    pip install -r "$ROOT/test/requirements.txt"
    cd "$ROOT"
    # TODO: run tests
fi

# Optionally, build the documentation
if [ -v LIBCARNA_PYTHON_BUILD_DOCS ]; then
    pip install -r "$ROOT"/docs/requirements.txt
    export LIBCARNA_PYTHON_PATH="$ROOT"/build
    rm -rf "$ROOT"/docs/build
    sphinx-build -M html "$ROOT"/docs "$ROOT"/docs/build
    cp "$ROOT/docs/build/html/examples/"*.ipynb "$ROOT"/examples/
fi