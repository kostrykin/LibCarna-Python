#!/bin/bash
set -ex

if [ -z "$LIBCARNA_SRC_PREFIX" ]; then
    echo "LIBCARNA_SRC_PREFIX is not set."
    exit 1
fi
export ROOT=$PWD/$(dirname "$0")
export LIBCARNA_INSTALL_PREFIX="$ROOT/.libcarna-dev"

# Build development version of LibCarna
cd "$LIBCARNA_SRC_PREFIX"
export BUILD=only_release
export LIBCARNA_NO_INSTALL=1
export CMAKE_ARGS="-DCMAKE_INSTALL_PREFIX=$LIBCARNA_INSTALL_PREFIX $CMAKE_ARGS"
export CMAKE_ARGS="-DINSTALL_CMAKE_DIR=$LIBCARNA_INSTALL_PREFIX $CMAKE_ARGS"
export CMAKE_ARGS="-DTARGET_NAME_SUFFIX=-dev $CMAKE_ARGS"
bash linux_build-egl.bash

cd build/make_release
make install
