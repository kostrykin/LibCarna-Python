#include <memory>

#include <Carna/Carna.h>
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

    Surface( const Carna::base::GLContext& glContext, unsigned int width, unsigned int height );

    virtual ~Surface();

    unsigned int width() const;

    unsigned int height() const;

    const Carna::base::GLContext& glContext;

    void begin() const;

    const unsigned char* end() const;

    const std::size_t& size;

}; // Surface



}  // namespace Carna :: py

}  // namespace Carna

