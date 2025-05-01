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

class MIPStageView;



// ----------------------------------------------------------------------------------
// OpaqueRenderingStageView
// ----------------------------------------------------------------------------------

class OpaqueRenderingStageView : public Carna::py::base::MeshRenderingStageView
{

public:

    explicit OpaqueRenderingStageView( unsigned int geometryType );

}; // OpaqueRenderingStageView



// ----------------------------------------------------------------------------------
// VolumeRenderingStageView
// ----------------------------------------------------------------------------------

class VolumeRenderingStageView : public Carna::py::base::RenderStageView
{

public:

    const static unsigned int DEFAULT_SAMPLE_RATE;

    explicit VolumeRenderingStageView( Carna::presets::VolumeRenderingStage* renderStage );

    Carna::presets::VolumeRenderingStage& volumeRenderingStage();

}; // VolumeRenderingStageView



// ----------------------------------------------------------------------------------
// MaskRenderingStageView
// ----------------------------------------------------------------------------------

class MaskRenderingStageView : public VolumeRenderingStageView
{

public:

    explicit MaskRenderingStageView( unsigned int geometryType, unsigned int maskRole );

    Carna::presets::MaskRenderingStage& maskRenderingStage();

}; // MaskRenderingStageView



// ----------------------------------------------------------------------------------
// MIPStageView
// ----------------------------------------------------------------------------------

class MIPStageView : public VolumeRenderingStageView
{

public:

    explicit MIPStageView( unsigned int geometryType );

    Carna::presets::MIPStage& mipStage();

    std::shared_ptr< base::ColorMapView > colorMap();

}; // MIPStageView



// ----------------------------------------------------------------------------------
// CuttingPlanesStageView
// ----------------------------------------------------------------------------------

class CuttingPlanesStageView : public Carna::py::base::RenderStageView
{

public:

    explicit CuttingPlanesStageView( unsigned int volumeGeometryType, unsigned int planeGeometryType );

    Carna::presets::CuttingPlanesStage& cuttingPlanesStage();

}; // CuttingPlanesStageView



}  // namespace Carna :: py :: presets

}  // namespace Carna :: py

}  // namespace Carna