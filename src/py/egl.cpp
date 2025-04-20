#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/egl/EGLContext.h>
#include <Carna/py/egl.h>

using namespace Carna::py::egl;



// ----------------------------------------------------------------------------------
// EGLContextView
// ----------------------------------------------------------------------------------

EGLContextView::EGLContextView()
    : Carna::py::base::GLContextView( Carna::egl::EGLContext::create() )
{
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: egl
// ----------------------------------------------------------------------------------

#ifdef BUILD_EGL_MODULE
PYBIND11_MODULE( egl, m )
{

    py::class_< EGLContextView, std::shared_ptr< EGLContextView >, Carna::py::base::GLContextView >( m, "EGLContext" )
        .def( py::init<>() );

}
#endif // BUILD_EGL_MODULE