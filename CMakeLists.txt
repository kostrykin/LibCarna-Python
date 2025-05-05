cmake_minimum_required( VERSION 3.5 )
project( LibCarna-Python )
set( PYTHON_MODULE_NAME "libcarna" )
include( FindPackageHandleStandardArgs )

set( CMAKE_CXX_STANDARD 14 )
set( CMAKE_CXX_STANDARD_REQUIRED ON )
set( CMAKE_INTERPROCEDURAL_OPTIMIZATION FALSE )

############################################

set( FULL_VERSION ${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION} )
set( TARGET_NAME ${PROJECT_NAME}-${FULL_VERSION} )
string( TOUPPER ${PROJECT_NAME} PROJECT_NAME_CAPS )
string( REGEX REPLACE "-" "_" PROJECT_NAME_CAPS ${PROJECT_NAME_CAPS} )

set( CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYTHON_MODULE_NAME} )
set( CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYTHON_MODULE_NAME} )
set( CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYTHON_MODULE_NAME} )

############################################
# Set default options for this build
############################################

option( BUILD_TEST "Build the test suite" OFF )

############################################
# Macro that sets variable to default value
# only when the variable isn't defined yet
############################################

macro( option_default_to var_name default_val var_type doc_string )
    if( NOT DEFINED ${var_name} )
        set( ${var_name} ${default_val} )
    endif()
    set( ${var_name} ${${var_name}} CACHE ${var_type} ${doc_string} FORCE )
endmacro()

############################################
# Locate Find<ModuleName>.cmake scripts
############################################

list( APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/misc/CMake-Modules )
list( PREPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/.libcarna-dev )

############################################
# Define default paths for the installation
############################################

# set default library and header destinations (relative to CMAKE_INSTALL_PREFIX)
option_default_to( INSTALL_LIBRARY_DIR "${PROJECT_NAME}" String "Installation directory for libraries" )

############################################
# Normalize installation paths
# (get rid of Windows-style delimiters)
############################################

file( TO_CMAKE_PATH ${INSTALL_LIBRARY_DIR} INSTALL_LIBRARY_DIR )

############################################
# Find required dependencies
############################################

# EGL
find_package( OpenGL REQUIRED COMPONENTS EGL )
include_directories( ${OPENGL_EGL_INCLUDE_DIRS} )

# pybind11
find_package( pybind11 REQUIRED )

# Eigen
find_package( Eigen3 REQUIRED )
include_directories( ${EIGEN3_INCLUDE_DIR} )

# LibCarna
find_package( LibCarna ${REQUIRED_VERSION_LIBCARNA} REQUIRED COMPONENTS release )
include_directories( ${LibCarna_INCLUDE_DIR} )
set( LIBCARNA_VERSION ${FOUND_VERSION} )

############################################

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/misc/__init__.py.in
                ${CMAKE_CURRENT_BINARY_DIR}/${PYTHON_MODULE_NAME}/__init__.py @ONLY )

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/misc/py.py
                ${CMAKE_CURRENT_BINARY_DIR}/${PYTHON_MODULE_NAME}/py.py COPYONLY )

file( GLOB LICENSES "${LibCarna_LICENSE_DIR}/LICENSE*" )
file( COPY ${LICENSES} DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/licenses/" )

############################################
# Project
############################################

include_directories( ${CMAKE_PROJECT_DIR}src/include )
set( MODULES
        base
        egl
        presets
        helpers
    )
set( SRC
        src/egl/EGLContext.cpp
        src/py/log.cpp
        src/py/Surface.cpp
        src/py/base.cpp
        src/py/egl.cpp
        src/py/presets.cpp
        src/py/helpers.cpp
    )

############################################
# Add sources
############################################

foreach( MODULE ${MODULES} )
    string( TOUPPER ${MODULE} MODULE_CAPS )
    pybind11_add_module( ${MODULE} ${SRC} )
    target_compile_options( ${MODULE} PRIVATE -fvisibility=default -fno-lto )
    target_compile_definitions( ${MODULE} PRIVATE )
    SET_TARGET_PROPERTIES( ${MODULE} PROPERTIES PREFIX "" )
endforeach( MODULE )

add_definitions( -D${PROJECT_NAME_CAPS}_EXPORT -DNOMINMAX )

############################################
# Add dependencies to the linker
############################################

include( "misc/compiler_specific.cmake" )

foreach( MODULE ${MODULES} )
    target_link_libraries(
        ${MODULE}
        PRIVATE
        ${OPENGL_LIBRARIES}
        ${LibCarna_LIBRARIES}
        OpenGL::EGL
    )
endforeach( MODULE )

############################################
# Define installation routines
############################################

install( TARGETS ${MODULES}
    RUNTIME DESTINATION ${INSTALL_LIBRARY_DIR}
    ARCHIVE DESTINATION ${INSTALL_LIBRARY_DIR}
    LIBRARY DESTINATION ${INSTALL_LIBRARY_DIR}
)

install( FILES
    ${CMAKE_CURRENT_BINARY_DIR}/${PYTHON_MODULE_NAME}/__init__.py
    DESTINATION ${INSTALL_LIBRARY_DIR}
)

############################################
# Process unit tests
############################################

if( BUILD_TEST )
    add_subdirectory( test )
endif()
