#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/egl/Context.h>
#include <Carna/py/py.h>

using namespace Carna::egl;



// ----------------------------------------------------------------------------------
// ContextView
// ----------------------------------------------------------------------------------

class ContextView : public std::enable_shared_from_this< ContextView >
{

public:

    const std::unique_ptr< Context > context;

    explicit ContextView( Context* context );

    virtual ~ContextView();

}; // ContextView


ContextView::ContextView( Context* context )
    : context( std::unique_ptr< Context >( context ) )
{
/*
#if CARNA_EXTRA_CHECKS
debugEvent( context, "created" );
#endif // CARNA_EXTRA_CHECKS
*/
}


ContextView::~ContextView()
{
/*
#if CARNA_EXTRA_CHECKS
debugEvent( context, "deleted" );
#endif // CARNA_EXTRA_CHECKS
*/
}



PYBIND11_MODULE( egl, m )
{

    py::class_< ContextView, std::shared_ptr< ContextView > >( m, "Context" )
        .def( py::init<>(
                []()
                {
                    return new ContextView( Context::create() );
                }
            )
        );

}

