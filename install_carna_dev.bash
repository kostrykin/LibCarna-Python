#!/bin/bash
set -ex

if [ -z "$CARNA_SRC_PREFIX" ]; then
    echo "CARNA_SRC_PREFIX is not set."
    exit 1
fi
export ROOT=$(dirname "$0")
export CARNA_INSTALL_PREFIX="$ROOT/.carna-dev"

# Build development version of Carna
cd "$CARNA_SRC_PREFIX"
export BUILD=only_release
export CARNA_NO_INSTALL=1
export CMAKE_ARGS="-DCMAKE_INSTALL_PREFIX=$CARNA_INSTALL_PREFIX $CMAKE_ARGS"
export CMAKE_ARGS="-DINSTALL_CMAKE_DIR=$CARNA_INSTALL_PREFIX $CMAKE_ARGS"
bash linux_build-egl.bash

cd build/make_release
make install
