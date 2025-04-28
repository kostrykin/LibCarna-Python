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
// MIPLayerView
// ----------------------------------------------------------------------------------

class MIPLayerView : public std::enable_shared_from_this< MIPLayerView >
{

public:

    template< typename... Args >
    explicit MIPLayerView( Args... args );

    virtual ~MIPLayerView();

    Carna::presets::MIPLayer* mipLayer;

    std::shared_ptr< MIPStageView > ownedBy;

}; // MIPStageView


template< typename... Args >
MIPLayerView::MIPLayerView( Args... args )
    : mipLayer( new Carna::presets::MIPLayer( args... ) )
{
}



// ----------------------------------------------------------------------------------
// MIPStageView
// ----------------------------------------------------------------------------------

class MIPStageView : public VolumeRenderingStageView
{

public:

    explicit MIPStageView( unsigned int geometryType );

    Carna::presets::MIPStage& mipStage();

    void appendLayer( MIPLayerView* mipLayerView );

    void removeLayer( MIPLayerView& mipLayerView );

}; // MIPStageView



}  // namespace Carna :: py :: presets

}  // namespace Carna :: py

}  // namespace Carna