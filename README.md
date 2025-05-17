LibCarna-Python
===============

The aim of this package is to provide real-time 3D visualization in Python for specifically, but not limited to, biomedical data. The library is based on [LibCarna](https://github.com/kostrykin/LibCarna).

See [libcarna.readthedocs.io](https://libcarna.readthedocs.io) for examples and documentation.

[![Build and Test](https://github.com/kostrykin/LibCarna-Python/actions/workflows/build_all.yml/badge.svg)](https://github.com/kostrykin/LibCarna-Python/actions/workflows/build_all.yml)
[![Anaconda-Server Badge](https://img.shields.io/badge/Install%20with-conda-%2387c305)](https://anaconda.org/bioconda/libcarna-python)
[![Anaconda-Server Badge](https://img.shields.io/conda/v/bioconda/libcarna-python.svg?label=Version)](https://anaconda.org/bioconda/libcarna-python)
[![Anaconda-Server Badge](https://img.shields.io/conda/pn/bioconda/libcarna-python.svg?label=Platforms)](https://anaconda.org/bioconda/libcarna-python)

---
## Contents

* [Limitations](#1-limitations)
* [Dependencies](#2-dependencies)
* [Installation](#3-installation)
* [Build instructions](#4-build-instructions)
 
---
## 1. Limitations

* Only 8bit and 16bit volume data are supported at the moment.
* Only a subset of rendering stages is exposed to Python yet.
* Build process is currently limited to Linux-based systems.

---
## 2. Dependencies

General dependencies are listed in *environment.yml*. Further dependencies for testing are listed in
*test/requirements.txt*, and those for the documentation in *docs/requirements.txt*.

---
## 3. Installation

The easiest way to install and use the library is to use one of the binary [Conda](https://www.anaconda.com/docs/getting-started/miniconda) packages:

```bash
conda install bioconda::libcarna-python
```

If you encounter an error that looks like below,

> Failed expression: pimpl->eglDpy != EGL_NO_DISPLAY

then you must install the EGL implementation suitable for your rendering hardware (e.g., `sudo apt install libegl1`
installs a meta package that automatically chooses the right implementation, or `libegl-mesa0` for software rendering).

---
## 4. Build instructions

There is a build script for Ubuntu Linux which builds a wheel file:
```bash
LIBCARNA_PYTHON_BUILD_DOCS=1 LIBCARNA_PYTHON_BUILD_TESTS=1 ./linux_build.bash
```
Adaption to other distributions should be self-explanatory.

After building the wheel file, it can be installed using:
```bash
pip install --force-reinstall build/dist/libcarna_python-*.whl
```

To build against a development version of [LibCarna](https://github.com/kostrykin/LibCarna), install it locally via
```bash
LIBCARNA_SRC_PREFIX="../LibCarna" ./install_libcarna_dev.bash
```
where you make `LIBCARNA_SRC_PREFIX` point to the source directory.

This will create a local directory `.libcarna-dev`. The build process will give precedence to LibCarna from this directory over other versions. Simply remove `.libcarna-dev` to stop building agaisnt the development version of LibCarna.
