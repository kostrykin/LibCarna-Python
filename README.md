LibCarna-Python
===============

The aim of this package is to provide real-time 3D visualization in Python for specifically, but not limited to, biomedical data. The library is based on [LibCarna](https://github.com/kostrykin/LibCarna).

See [examples/kalinin2018.ipynb](examples/kalinin2018.ipynb) for an example.

[![Build LibCarnaPy and Docker image](https://github.com/kostrykin/LibCarnaPy/actions/workflows/build.yml/badge.svg)](https://github.com/kostrykin/LibCarnaPy/actions/workflows/build.yml)
[![Anaconda-Server Badge](https://img.shields.io/badge/Install%20with-conda-%2387c305)](https://anaconda.org/kostrykin/carnapy)
[![Anaconda-Server Badge](https://img.shields.io/conda/v/kostrykin/carnapy.svg?label=Version)](https://anaconda.org/kostrykin/carnapy)
[![Anaconda-Server Badge](https://img.shields.io/conda/pn/kostrykin/carnapy.svg?label=Platforms)](https://anaconda.org/kostrykin/carnapy)

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

Using the library requires the following dependencies:
* [numpy](https://numpy.org/) ≥ 1.16
* EGL driver support
* OpenGL 3.3
* Python ≥ 3.9

The following dependencies must be satisfied for the build process:
* [LibCarna](https://github.com/kostrykin/LibCarna) ≥ 3.4
* [Eigen](http://eigen.tuxfamily.org/) ≥ 3.0.5
* [pybind11](https://github.com/pybind/pybind11)
* EGL development files

See environment.yml for further dependencies for testing and running.

---
## 3. Installation

The easiest way to install and use the library is to use one of the binary [Conda](https://www.anaconda.com/docs/getting-started/miniconda) packages:

```bash
conda install bioconda::libcarna-python
```

---
## 4. Build instructions

There is a build script for Ubuntu Linux which builds a wheel file:
```bash
LIBCARNA_PYTHON_BUILD_DOCS=ON LIBCARNA_PYTHON_BUILD_TEST=ON ./linux_build.bash
```
Adaption to other distribution should be self-explanatory.

After building the wheel file, it can be installed using:
```bash
python -m pip install --force-reinstall $(find . -name 'LibCarna_Python*.whl')
```

To build against a development version of LibCarna, install it locally,
```bash
LIBCARNA_SRC_PREFIX="../LibCarna" ./install_libcarna_dev.bash
```
where you make `LIBCARNA_SRC_PREFIX` point to the source directory.

This will create a local directory `.libcarna-dev`. The build process will give precedence to LibCarna from this directory over other versions. Simply remove `.libcarna-dev` to stop building agaisnt the development version of LibCarna.
