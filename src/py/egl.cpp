#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/egl/Context.h>
#include <Carna/py/py.h>

using namespace Carna::egl;



PYBIND11_MODULE( egl, m )
{

    py::class_< Context, Carna::base::GLContext >( m, "Context" )
        .def_static( "create", &Context::create );

}

