#pragma once

#include <Carna/Carna.h>
#include <Carna/base/Material.h>

namespace Carna
{

namespace py
{

namespace base
{



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



}  // namespace Carna :: py :: base

}  // namespace Carna :: py

}  // namespace Carna