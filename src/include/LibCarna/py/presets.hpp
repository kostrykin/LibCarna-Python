#pragma once

#include <LibCarna/LibCarna.hpp>
#include <LibCarna/presets/OpaqueRenderingStage.hpp>
#include <LibCarna/py/base.hpp>

namespace LibCarna
{

namespace py
{

namespace presets
{

class MIPStageView;



// ----------------------------------------------------------------------------------
// OpaqueRenderingStageView
// ----------------------------------------------------------------------------------

class OpaqueRenderingStageView : public LibCarna::py::base::MeshRenderingStageView
{

public:

    explicit OpaqueRenderingStageView( unsigned int geometryType );

    LibCarna::presets::OpaqueRenderingStage& opaqueRenderingStage();

}; // OpaqueRenderingStageView



// ----------------------------------------------------------------------------------
// VolumeRenderingStageView
// ----------------------------------------------------------------------------------

class VolumeRenderingStageView : public LibCarna::py::base::RenderStageView
{

public:

    const static unsigned int DEFAULT_SAMPLE_RATE;

    explicit VolumeRenderingStageView( LibCarna::presets::VolumeRenderingStage* renderStage );

    LibCarna::presets::VolumeRenderingStage& volumeRenderingStage();

}; // VolumeRenderingStageView



// ----------------------------------------------------------------------------------
// MaskRenderingStageView
// ----------------------------------------------------------------------------------

class MaskRenderingStageView : public VolumeRenderingStageView
{

public:

    explicit MaskRenderingStageView( unsigned int geometryType, unsigned int maskRole );

    LibCarna::presets::MaskRenderingStage& maskRenderingStage();

}; // MaskRenderingStageView



// ----------------------------------------------------------------------------------
// MIPStageView
// ----------------------------------------------------------------------------------

class MIPStageView : public VolumeRenderingStageView
{

public:

    explicit MIPStageView( unsigned int geometryType, unsigned int colorMapResolution );

    LibCarna::presets::MIPStage& mipStage();

    std::shared_ptr< base::ColorMapView > colorMap();

}; // MIPStageView



// ----------------------------------------------------------------------------------
// CuttingPlanesStageView
// ----------------------------------------------------------------------------------

class CuttingPlanesStageView : public LibCarna::py::base::RenderStageView
{

public:

    explicit CuttingPlanesStageView
        ( unsigned int volumeGeometryType
        , unsigned int planeGeometryType
        , unsigned int colorMapResolution );

    LibCarna::presets::CuttingPlanesStage& cuttingPlanesStage();

    std::shared_ptr< base::ColorMapView > colorMap();

}; // CuttingPlanesStageView



// ----------------------------------------------------------------------------------
// DVRStageView
// ----------------------------------------------------------------------------------

class DVRStageView : public VolumeRenderingStageView
{

public:

    explicit DVRStageView( unsigned int geometryType, unsigned int colorMapResolution );

    LibCarna::presets::DVRStage& dvrStage();

    std::shared_ptr< base::ColorMapView > colorMap();

}; // DVRStageView



// ----------------------------------------------------------------------------------
// DRRStage
// ----------------------------------------------------------------------------------

class DRRStageView : public VolumeRenderingStageView
{

public:

    explicit DRRStageView( unsigned int geometryType );

    LibCarna::presets::DRRStage& drrStage();

}; // DRRStageView



}  // namespace LibCarna :: py :: presets

}  // namespace LibCarna :: py

}  // namespace LibCarna