#pragma once

#include <LibCarna/LibCarna.hpp>
#include <LibCarna/base/Node.hpp>
#include <LibCarna/base/Material.hpp>
#include <LibCarna/base/FrameRenderer.hpp>

namespace LibCarna
{

namespace py
{

namespace base
{


class FrameRendererView;



// ----------------------------------------------------------------------------------
// VIEW_DELEGATE
// ----------------------------------------------------------------------------------

#define VIEW_DELEGATE( ViewType, delegate, ... ) \
    []( ViewType& self __VA_OPT__( , __VA_ARGS__ ) ) \
    { \
        return self.delegate; \
    }



// ----------------------------------------------------------------------------------
// VIEW_DELEGATE_RETURN_SELF
// ----------------------------------------------------------------------------------

#define VIEW_DELEGATE_RETURN_SELF( ViewType, delegate, ... ) \
    []( ViewType& self __VA_OPT__( , __VA_ARGS__ ) ) \
    { \
        self.delegate; \
        return self; \
    }



// ----------------------------------------------------------------------------------
// GLContextView
// ----------------------------------------------------------------------------------

class GLContextView : public std::enable_shared_from_this< GLContextView >
{

public:

    const std::unique_ptr< LibCarna::base::GLContext > context;

    explicit GLContextView( LibCarna::base::GLContext* context );

    virtual ~GLContextView();

}; // GLContextView



// ----------------------------------------------------------------------------------
// SpatialView
// ----------------------------------------------------------------------------------

class SpatialView : public std::enable_shared_from_this< SpatialView >
{

public:

    /* The view that owns the spatial object of this view. The spatial object of this view is owned by this view, if it
     * is not owned by any other spatial object.
     */
    std::shared_ptr< SpatialView > ownedBy;

    /* The spatial object of this view.
     */
    LibCarna::base::Spatial* const spatial;

    explicit SpatialView( LibCarna::base::Spatial* spatial );

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

    explicit NodeView( LibCarna::base::Node* node );

    virtual ~NodeView();

    LibCarna::base::Node& node();

    void attachChild( SpatialView& child );

    /* Locks objects with shared ownership until this node view dies.
     *
     * When this node view dies, and the spatial objects of this view is owned by another view, the locked objects are
     * propagated to the view that owns the spatial objects of this view.
     */
    std::unordered_set< std::shared_ptr< void > > locks;

}; // NodeView


template< typename... Args >
NodeView::NodeView( Args... args )
    : SpatialView::SpatialView( new LibCarna::base::Node( args... ) )
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

    LibCarna::base::Camera& camera();

}; // CameraView


template< typename... Args >
CameraView::CameraView( Args... args )
    : SpatialView::SpatialView( new LibCarna::base::Camera( args... ) )
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

    LibCarna::base::Geometry& geometry();

}; // GeometryView


template< typename... Args >
GeometryView::GeometryView( Args... args )
    : SpatialView::SpatialView( new LibCarna::base::Geometry( args... ) )
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
    LibCarna::base::GeometryFeature& geometryFeature;

    explicit GeometryFeatureView( LibCarna::base::GeometryFeature& geometryFeature );

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

    LibCarna::base::Material& material();

    template< typename ParameterType >
    void setParameter( const std::string& name, const ParameterType& value );

}; // MaterialView


template< typename... Args >
MaterialView::MaterialView( Args... args )
    : GeometryFeatureView::GeometryFeatureView( LibCarna::base::Material::create( args... ) )
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
    LibCarna::base::RenderStage* const renderStage;

    explicit RenderStageView( LibCarna::base::RenderStage* renderStage );

    virtual ~RenderStageView();

}; // RenderStageView



// ----------------------------------------------------------------------------------
// MeshRenderingStageView
// ----------------------------------------------------------------------------------

class MeshRenderingStageView : public LibCarna::py::base::RenderStageView
{

public:

    const static unsigned int ROLE_DEFAULT_MESH;
    const static unsigned int ROLE_DEFAULT_MATERIAL;

    explicit MeshRenderingStageView( LibCarna::base::RenderStage* renderStage );

}; // MeshRenderingStageView



// ----------------------------------------------------------------------------------
// FrameRendererView
// ----------------------------------------------------------------------------------

class FrameRendererView : public std::enable_shared_from_this< FrameRendererView >
{

public:

    const std::shared_ptr< GLContextView > context;

    LibCarna::base::FrameRenderer frameRenderer;

    FrameRendererView
        ( GLContextView& context
        , unsigned int width
        , unsigned int height
        , bool fitSquare );

    void appendStage( const std::shared_ptr< RenderStageView >& rsView );

    virtual ~FrameRendererView();

}; // FrameRendererView



// ----------------------------------------------------------------------------------
// ColorMapView
// ----------------------------------------------------------------------------------

class ColorMapView : public std::enable_shared_from_this< ColorMapView >
{

public:

    const std::shared_ptr< RenderStageView > ownedBy;

    LibCarna::base::ColorMap& colorMap;

    ColorMapView( const std::shared_ptr< RenderStageView >& ownedBy, LibCarna::base::ColorMap& colorMap );

}; // ColorMapView



// ----------------------------------------------------------------------------------
// MeshFactoryView
// ----------------------------------------------------------------------------------

class MeshFactoryView
{
}; // MeshFactoryView



}  // namespace LibCarna :: py :: base

}  // namespace LibCarna :: py

}  // namespace LibCarna