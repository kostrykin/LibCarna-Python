CarnaPy
========

The aim of this package is to provide real-time 3D visualization in Python for specifically, but not limited to, biomedical data. The library is based on [Carna](https://github.com/kostrykin/Carna).

See [examples/kalinin2018.ipynb](examples/kalinin2018.ipynb) for an example.

[![Build CarnaPy and Docker image](https://github.com/kostrykin/CarnaPy/actions/workflows/build.yml/badge.svg)](https://github.com/kostrykin/CarnaPy/actions/workflows/build.yml)
![Docker Image Version (latest semver)](https://img.shields.io/docker/v/kostrykin/carnapy?label=DockerHub%3A)
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
* DRR renderings are not exposed to Python yet.
* Build process is currently limited to Linux-based systems.

---
## 2. Dependencies

Using the library requires the following dependencies:
* [numpy](https://numpy.org/) ≥ 1.16
* EGL driver support
* OpenGL 3.3
* Python ≥ 3.7

The following dependencies must be satisfied for the build process:
* [Carna](https://github.com/kostrykin/Carna) ≥ 3.1
* [Eigen](http://eigen.tuxfamily.org/) ≥ 3.0.5
* [libboost-iostreams](https://www.boost.org/doc/libs/1_76_0/libs/iostreams/doc/index.html)
* [pybind11](https://github.com/pybind/pybind11)
* EGL development files

In addition, the following dependencies are required to run the test suite:
* [matplotlib](https://matplotlib.org/)
* [scipy](https://www.scipy.org/)

---
## 3. Installation

The easiest way to install and use the library is to use one of the binary [Conda](https://docs.anaconda.com/anaconda/install/) packages:

```bash
conda install -c kostrykin carnapy
```

Conda packages are available for Python 3.7–3.9.

---
## 4. Build instructions

There is a build script for Ubuntu Linux which builds a wheel file:
```bash
CARNAPY_BUILD_DOCS=ON CARNAPY_BUILD_TEST=ON ./linux_build.bash
```
Adaption to other distribution should be self-explanatory.

After building the wheel file, it can be installed using:
```bash
python -m pip install --force-reinstall $(find . -name 'CarnaPy*.whl')
```

To build against a development version of Carna, install it locally,
```bash
CARNA_SRC_PREFIX="../Carna" ./install_carna_dev.bash
```
where you make `CARNA_SRC_PREFIX` point to the source directory.

This will create a local directory `.carna-dev`. The build process will give precedence to Carna from this directory over other versions. Simply remove `.carna-dev` to stop building agaisnt the development version of Carna.
