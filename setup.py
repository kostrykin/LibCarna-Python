# Build and install:
# > python setup.py bdist_wheel
# > python -m pip install --force-reinstall LibCarna_Python/dist/*.whl
# 
# Distribute to PyPI:
# > python setup.py sdist
# > python -m twine upload dist/*.tar.gz

import os
import sys
from pathlib import Path

import yaml

with open('misc/versions.yml', 'r') as io:
    versions = yaml.safe_load(io)

VERSION_LIBCARNA_PYTHON = versions['build']['LibCarna-Python']
VERSION_LIBCARNA = versions['build']['LibCarna']

root_dir = Path(os.path.abspath(os.path.dirname(__file__)))

build_dirs = dict(
    debug   = root_dir / 'build' / 'make_debug',
    release = root_dir / 'build' / 'make_release',
)

if __name__ == '__main__':

    (build_dirs['debug']   / 'libcarna').mkdir(parents=True, exist_ok=True)
    (build_dirs['release'] / 'libcarna').mkdir(parents=True, exist_ok=True)

    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext as build_ext_orig

    with open(root_dir / 'README.md', encoding='utf-8') as io:
        long_description = io.read()

    class CMakeExtension(Extension):

        def __init__(self):
            super().__init__('CMake', sources=[])

    class build_ext(build_ext_orig):

        def run(self):
            for ext in self.extensions:
                self.build_cmake(ext)

        def build_cmake(self, ext):
            version_major, version_minor, version_patch = [int(val) for val in VERSION_LIBCARNA_PYTHON.split('.')]
            build_test = os.environ.get('LIBCARNA_PYTHON_BUILD_TEST', 'ON')
            assert build_test in ('ON', 'OFF')
            build_type = os.environ.get('CMAKE_BUILD_TYPE', 'Release')
            cmake_args = [
                f'-DCMAKE_BUILD_TYPE={build_type}',
                f'-DBUILD_TEST={build_test}',
                f'-DMAJOR_VERSION={version_major}',
                f'-DMINOR_VERSION={version_minor}',
                f'-DPATCH_VERSION={version_patch}',
                f'-DREQUIRED_VERSION_LIBCARNA={VERSION_LIBCARNA}',
                f'-DPYTHON_EXECUTABLE={sys.executable}',
                f'-Dpybind11_DIR={os.environ["PYBIND11_PREFIX"]}',
                f'-DCMAKE_MODULE_PATH={os.environ.get("CMAKE_MODULE_PATH")}',
                f'../..',
            ]

            if not self.dry_run:

                os.chdir(str(build_dirs[build_type.lower()]))
                self.spawn(['cmake'] + cmake_args)
                self.spawn(['make', 'VERBOSE=1'])
                if build_test == 'ON':
                    self.spawn(['make', 'RUN_TESTSUITE'])

            os.chdir(str(root_dir))

    setup(
        name = 'LibCarna-Python',
        version = VERSION_LIBCARNA_PYTHON,
        description = 'General-purpose real-time 3D visualization',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        author = 'Leonid Kostrykin',
        author_email = 'leonid.kostrykin@bioquant.uni-heidelberg.de',
        url = 'https://github.com/kostrykin/LibCarna-Python',
        include_package_data = True,
        license = 'MIT',
        license_files = [
            'LICENSE',
            'build/make_release/licenses/LICENSE-Carna',
            'build/make_release/licenses/LICENSE-LibCarna',
            'build/make_release/licenses/LICENSE-Eigen',
            'build/make_release/licenses/LICENSE-GLEW',
        ],
        package_dir = {
            'libcarna': 'build/make_release/libcarna',
        },
        packages = ['libcarna'],
        package_data = {
            'libcarna': ['*.so'],
        },
        ext_modules = [CMakeExtension()],
        cmdclass={
            'build_ext': build_ext,
        },
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: GPU',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Topic :: Education',
            'Topic :: Multimedia :: Graphics :: 3D Rendering',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: User Interfaces',
        ],
        install_requires = [
            'numpy',
        ],
    )

