#pragma once

#include <Carna/Carna.h>
#include <Carna/presets/OpaqueRenderingStage.h>
#include <Carna/py/base.h>

namespace Carna
{

namespace py
{

namespace presets
{



// ----------------------------------------------------------------------------------
// OpaqueRenderingStageView
// ----------------------------------------------------------------------------------

class OpaqueRenderingStageView : public Carna::py::base::MeshRenderingStageView
{

public:

    explicit OpaqueRenderingStageView( unsigned int geometryType );

}; // OpaqueRenderingStageView



}  // namespace Carna :: py :: presets

}  // namespace Carna :: py

}  // namespace Carna