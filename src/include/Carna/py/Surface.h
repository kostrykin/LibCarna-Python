#pragma once

#include <memory>

#include <pybind11/numpy.h>

#include <Carna/py/base.h>
#include <Carna/base/noncopyable.h>

namespace Carna
{

namespace py
{



// ----------------------------------------------------------------------------------
// Surface
// ----------------------------------------------------------------------------------

class Surface
{

    NON_COPYABLE

    struct Details;
    const std::unique_ptr< Details > pimpl;

public:

    Surface( const Carna::py::base::GLContextView& contextView, unsigned int width, unsigned int height );

    virtual ~Surface();

    unsigned int width() const;

    unsigned int height() const;

    const std::shared_ptr< const Carna::py::base::GLContextView > contextView;

    void begin() const;

    pybind11::array end() const;

    const std::size_t& size;

}; // Surface



}  // namespace Carna :: py

}  // namespace Carna

