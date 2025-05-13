#pragma once

#include <LibCarna/py/base.hpp>
#include <LibCarna/egl/EGLContext.hpp>

namespace LibCarna
{

namespace py
{

namespace egl
{



// ----------------------------------------------------------------------------------
// EGLContextView
// ----------------------------------------------------------------------------------

class EGLContextView : public LibCarna::py::base::GLContextView
{

public:

    EGLContextView();

    LibCarna::egl::EGLContext& eglContext() const;

}; // EGLContextView



}  // namespace LibCarna :: py :: egl

}  // namespace LibCarna :: py

}  // namespace LibCarna