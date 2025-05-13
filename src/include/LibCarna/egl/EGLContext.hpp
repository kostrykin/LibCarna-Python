#pragma once

#include <LibCarna/base/GLContext.hpp>
#include <LibCarna/base/noncopyable.hpp>

namespace LibCarna
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

    const std::string& vendor() const;

    const std::string& renderer() const;

protected:

    virtual void activate() const;

}; // EGLContext



}  // namespace LibCarna :: egl

}  // namespace LibCarna

