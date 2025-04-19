#include <Carna/base/GLContext.h>
#include <Carna/base/noncopyable.h>

namespace Carna
{

namespace egl
{



// ----------------------------------------------------------------------------------
// EGLContext
// ----------------------------------------------------------------------------------

class EGLContext : public base::GLContext
{

    NON_COPYABLE

    struct Details;
    const std::unique_ptr< Details > pimpl;

    EGLContext( Details* );

public:

    static EGLContext* create();

    virtual ~EGLContext();

protected:

    virtual void activate() const;

}; // EGLContext



}  // namespace Carna :: egl

}  // namespace Carna

