#pragma once

#include <memory>

#include <pybind11/numpy.h>

#include <LibCarna/py/base.hpp>
#include <LibCarna/base/noncopyable.hpp>

namespace LibCarna
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

    Surface( const LibCarna::py::base::GLContextView& contextView, unsigned int width, unsigned int height );

    virtual ~Surface();

    unsigned int width() const;

    unsigned int height() const;

    const std::shared_ptr< const LibCarna::py::base::GLContextView > contextView;

    void begin() const;

    pybind11::array_t< unsigned char > end() const;

    const std::size_t& size;

}; // Surface



}  // namespace LibCarna :: py

}  // namespace LibCarna

