#pragma once

#include <LibCarna/py/base.hpp>

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

}; // EGLContextView



}  // namespace LibCarna :: py :: egl

}  // namespace LibCarna :: py

}  // namespace LibCarna