#pragma once

#include <Carna/Carna.h>
#include <Carna/base/Material.h>
#include <Carna/base/FrameRenderer.h>

namespace Carna
{

namespace py
{

namespace base
{


class FrameRendererView;



// ----------------------------------------------------------------------------------
// GLContextView
// ----------------------------------------------------------------------------------

class GLContextView : public std::enable_shared_from_this< GLContextView >
{

public:

    const std::unique_ptr< Carna::base::GLContext > context;

    explicit GLContextView( Carna::base::GLContext* context );

    virtual ~GLContextView();

}; // GLContextView



// ----------------------------------------------------------------------------------
// SpatialView
// ----------------------------------------------------------------------------------

class SpatialView : public std::enable_shared_from_this< SpatialView >
{

public:

    /* The object that owns the spatial object of this view. The spatial object of
     * this view is owned by the view, if it is not owned by any other spatial object.
     */
    std::shared_ptr< SpatialView > ownedBy;

    /* The spatial object of this view.
     */
    Carna::base::Spatial* const spatial;

    explicit SpatialView( Carna::base::Spatial* spatial );

    virtual ~SpatialView();

}; // SpatialView



// ----------------------------------------------------------------------------------
// NodeView
// ----------------------------------------------------------------------------------

class NodeView : public SpatialView
{

public:

    template< typename... Args >
    explicit NodeView( Args... args );

    Carna::base::Node& node();

    void attachChild( SpatialView& child );

}; // NodeView


template< typename... Args >
NodeView::NodeView( Args... args )
    : SpatialView::SpatialView( new Carna::base::Node( args... ) )
{
}



// ----------------------------------------------------------------------------------
// CameraView
// ----------------------------------------------------------------------------------

class CameraView : public SpatialView
{

public:

    template< typename... Args >
    explicit CameraView( Args... args );

    Carna::base::Camera& camera();

}; // CameraView


template< typename... Args >
CameraView::CameraView( Args... args )
    : SpatialView::SpatialView( new Carna::base::Camera( args... ) )
{
}



// ----------------------------------------------------------------------------------
// GeometryView
// ----------------------------------------------------------------------------------

class GeometryView : public SpatialView
{

public:

    template< typename... Args >
    explicit GeometryView( Args... args );

    Carna::base::Geometry& geometry();

}; // GeometryView


template< typename... Args >
GeometryView::GeometryView( Args... args )
    : SpatialView::SpatialView( new Carna::base::Geometry( args... ) )
{
}



// ----------------------------------------------------------------------------------
// GeometryFeatureView
// ----------------------------------------------------------------------------------

class GeometryFeatureView : public std::enable_shared_from_this< GeometryFeatureView >
{
public:

    /* The geometry feature of this view.
     */
    Carna::base::GeometryFeature& geometryFeature;

    explicit GeometryFeatureView( Carna::base::GeometryFeature& geometryFeature );

    virtual ~GeometryFeatureView();

}; // GeometryFeatureView



// ----------------------------------------------------------------------------------
// MaterialView
// ----------------------------------------------------------------------------------

class MaterialView : public GeometryFeatureView
{
public:

    template< typename... Args >
    explicit MaterialView( Args... args );

    Carna::base::Material& material();

    template< typename ParameterType >
    void setParameter( const std::string& name, const ParameterType& value );

}; // MaterialView


template< typename... Args >
MaterialView::MaterialView( Args... args )
    : GeometryFeatureView::GeometryFeatureView( Carna::base::Material::create( args... ) )
{
}


template< typename ParameterType >
void MaterialView::setParameter( const std::string& name, const ParameterType& value )
{
    material().setParameter( name, value );
}



// ----------------------------------------------------------------------------------
// RenderStageView
// ----------------------------------------------------------------------------------

class RenderStageView : public std::enable_shared_from_this< RenderStageView >
{

public:

    /* The object that owns the render stage of this view. The render Stage of this
     * view is owned by the view, if it is not owned by any \a FrameRendererView.
     */
    std::shared_ptr< FrameRendererView > ownedBy;

    /* The spatial object of this view.
     */
    Carna::base::RenderStage* const renderStage;

    explicit RenderStageView( Carna::base::RenderStage* renderStage );

    virtual ~RenderStageView();

}; // RenderStageView



// ----------------------------------------------------------------------------------
// MeshRenderingStageView
// ----------------------------------------------------------------------------------

class MeshRenderingStageView : public Carna::py::base::RenderStageView
{

public:

    const static unsigned int ROLE_DEFAULT_MESH;
    const static unsigned int ROLE_DEFAULT_MATERIAL;

    explicit MeshRenderingStageView( Carna::base::RenderStage* renderStage );

}; // MeshRenderingStageView



// ----------------------------------------------------------------------------------
// FrameRendererView
// ----------------------------------------------------------------------------------

class FrameRendererView : public std::enable_shared_from_this< FrameRendererView >
{

public:

    const std::shared_ptr< GLContextView > context;

    Carna::base::FrameRenderer frameRenderer;

    FrameRendererView
        ( GLContextView& context
        , unsigned int width
        , unsigned int height
        , bool fitSquare );

    /*
    static std::shared_ptr< FrameRendererView > create
        ( GLContextView& context
        , const std::vector< RenderStageView* >& renderStages
        , unsigned int width
        , unsigned int height
        , bool fitSquare );
    */

    virtual ~FrameRendererView();

}; // FrameRendererView



}  // namespace Carna :: py :: base

}  // namespace Carna :: py

}  // namespace Carna