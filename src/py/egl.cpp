#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <LibCarna/py/egl.hpp>

using namespace LibCarna::py::egl;



// ----------------------------------------------------------------------------------
// EGLContextView
// ----------------------------------------------------------------------------------

EGLContextView::EGLContextView()
    : LibCarna::py::base::GLContextView( LibCarna::egl::EGLContext::create() )
{
}


LibCarna::egl::EGLContext& EGLContextView::eglContext() const
{
    return static_cast< LibCarna::egl::EGLContext& >( *context );
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: egl
// ----------------------------------------------------------------------------------

PYBIND11_MODULE( egl, m )
{

    py::class_< EGLContextView, std::shared_ptr< EGLContextView >, LibCarna::py::base::GLContextView >( m, "EGLContext" )
        .def( py::init<>() )
        .def_property_readonly( "vendor", VIEW_DELEGATE( EGLContextView, eglContext().vendor() ) )
        .def_property_readonly( "renderer", VIEW_DELEGATE( EGLContextView, eglContext().renderer() ) )
        .doc() = "Create a :class:`carna.base.GLContext` using EGL (useful for off-screen rendering).";

}