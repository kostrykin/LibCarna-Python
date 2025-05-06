#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <LibCarna/base/FrameRenderer.hpp>
#include <LibCarna/base/Camera.hpp>
#include <LibCarna/base/Geometry.hpp>
#include <LibCarna/base/GeometryFeature.hpp>
#include <LibCarna/base/Color.hpp>
#include <LibCarna/base/ColorMap.hpp>
#include <LibCarna/base/BoundingVolume.hpp>
#include <LibCarna/base/GLContext.hpp>
#include <LibCarna/base/MeshFactory.hpp>
#include <LibCarna/base/RenderStage.hpp>
//#include <LibCarna/base/BlendFunction.hpp>
#include <LibCarna/base/MeshRenderingStage.hpp>
#include <LibCarna/py/base.hpp>
#include <LibCarna/py/Surface.hpp>
#include <LibCarna/py/log.hpp>

using namespace LibCarna::py;
using namespace LibCarna::py::base;



// ----------------------------------------------------------------------------------
// GLContextView
// ----------------------------------------------------------------------------------

GLContextView::GLContextView( LibCarna::base::GLContext* context )
    : context( context )
{
}


GLContextView::~GLContextView()
{
}



// ----------------------------------------------------------------------------------
// SpatialView
// ----------------------------------------------------------------------------------

SpatialView::SpatialView( LibCarna::base::Spatial* spatial )
    : ownedBy( nullptr )
    , spatial( spatial )
{
}


SpatialView::~SpatialView()
{
    if( ownedBy.get() == nullptr )
    {
        /* The spatial object of this view is not owned by any other spatial object,
         * thus it is safe to delete the object, when the last reference dies.
         */
         delete spatial;
    }
}



// ----------------------------------------------------------------------------------
// NodeView
// ----------------------------------------------------------------------------------

NodeView::NodeView( LibCarna::base::Node* node )
    : SpatialView::SpatialView( node )
{
}


NodeView::~NodeView()
{
    if( auto parentNodeView = std::dynamic_pointer_cast< NodeView >( ownedBy ) )
    {
        /* The spatial object of this view is owned by another spatial object, thus the locks are propagated.
         */
        parentNodeView->locks.insert( locks.begin(), locks.end() );
    }
}


LibCarna::base::Node& NodeView::node()
{
    return static_cast< LibCarna::base::Node& >( *spatial );
}


void NodeView::attachChild( SpatialView& child )
{
    /* Verify that the child is not already attached to another parent.
     */
    LIBCARNA_ASSERT_EX( !child.spatial->hasParent(), "Child already has a parent." );

    /* Check for circular relations (verify that `this` is not a child of `child`).
     */
    bool circular = false;
    if( LibCarna::base::Node* const childNode = dynamic_cast< LibCarna::base::Node* >( child.spatial ) )
    {
        childNode->visitChildren(
            true,
            [ &circular, this ]( const LibCarna::base::Spatial& spatial )
            {
                if( &spatial == this->spatial )
                {
                    circular = true;
                }
            }
        );
    }
    LIBCARNA_ASSERT_EX( !circular, "Circular relations are forbidden." );

    /* Update scene graph structure.
     */
    child.ownedBy = this->shared_from_this();
    this->node().attachChild( child.spatial );
}



// ----------------------------------------------------------------------------------
// CameraView
// ----------------------------------------------------------------------------------

LibCarna::base::Camera& CameraView::camera()
{
    return static_cast< LibCarna::base::Camera& >( *spatial );
}



// ----------------------------------------------------------------------------------
// GeometryView
// ----------------------------------------------------------------------------------

LibCarna::base::Geometry& GeometryView::geometry()
{
    return static_cast< LibCarna::base::Geometry& >( *spatial );
}



// ----------------------------------------------------------------------------------
// GeometryFeatureView
// ----------------------------------------------------------------------------------

GeometryFeatureView::GeometryFeatureView( LibCarna::base::GeometryFeature& geometryFeature )
    : geometryFeature( geometryFeature )
{
}


GeometryFeatureView::~GeometryFeatureView()
{
    geometryFeature.release();
}



// ----------------------------------------------------------------------------------
// MaterialView
// ----------------------------------------------------------------------------------

LibCarna::base::Material& MaterialView::material()
{
    return static_cast< LibCarna::base::Material& >( geometryFeature );
}



// ----------------------------------------------------------------------------------
// RenderStageView
// ----------------------------------------------------------------------------------

RenderStageView::RenderStageView( LibCarna::base::RenderStage* renderStage )
    : ownedBy( nullptr )
    , renderStage( renderStage )
{
}


RenderStageView::~RenderStageView()
{
    if( ownedBy.get() == nullptr )
    {
        /* The render stage of this view is not owned by any \a FrameRendererView,
         * thus it is safe to delete the object, when the last reference dies.
         */
         delete renderStage;
    }
}



// ----------------------------------------------------------------------------------
// MeshRenderingStageView
// ----------------------------------------------------------------------------------

const unsigned int MeshRenderingStageView::ROLE_DEFAULT_MESH = LibCarna::base::MeshRenderingMixin::ROLE_DEFAULT_MESH;
const unsigned int MeshRenderingStageView::ROLE_DEFAULT_MATERIAL = LibCarna::base::MeshRenderingMixin::ROLE_DEFAULT_MATERIAL;


MeshRenderingStageView::MeshRenderingStageView( LibCarna::base::RenderStage* renderStage )
    : RenderStageView::RenderStageView( renderStage )
{
}



// ----------------------------------------------------------------------------------
// FrameRendererView
// ----------------------------------------------------------------------------------

FrameRendererView::FrameRendererView
        ( GLContextView& context
        , unsigned int width
        , unsigned int height
        , bool fitSquare)
    : context( context.shared_from_this() )
    , frameRenderer( *( context.context ), width, height, fitSquare )
{
}


void FrameRendererView::appendStage( const std::shared_ptr< RenderStageView >& rsView )
{
    /* Verify that the render stage was not already added to another frame renderer.
     */
    LIBCARNA_ASSERT_EX( rsView->ownedBy.get() == nullptr, "Render stage was already added to a frame renderer." );

    /* Add the render stage to the frame renderer (and take ownership).
     */
    rsView->ownedBy = this->shared_from_this();
    frameRenderer.appendStage( rsView->renderStage );
}


FrameRendererView::~FrameRendererView()
{
}



// ----------------------------------------------------------------------------------
// ColorMapView
// ----------------------------------------------------------------------------------

ColorMapView::ColorMapView
    ( const std::shared_ptr< RenderStageView >& ownedBy
    , LibCarna::base::ColorMap& colorMap )

    : ownedBy( ownedBy )
    , colorMap( colorMap )
{
}



// ----------------------------------------------------------------------------------
// configureLog
// ----------------------------------------------------------------------------------

static void configureLog( bool enabled )
{
    if( enabled )
    {
        // TODO: use ::py::print to print log messages to `sys.stdout` so they can be tested
        // https://pybind11.readthedocs.io/en/stable/advanced/pycpp/utilities.html#using-python-s-print-function-in-c
        LibCarna::base::Log::instance().setWriter( new LibCarna::base::Log::StdWriter() );
    }
    else
    {
        LibCarna::base::Log::instance().setWriter( new NullWriter() );
    }
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: base
// ----------------------------------------------------------------------------------

PYBIND11_MODULE( base, m )
{

    py::register_exception< LibCarna::base::LibCarnaException >( m, "LibCarnaException" );
    py::register_exception< LibCarna::base::AssertionFailure >( m, "AssertionFailure" );

    m.def( "logging",
        []( bool enabled )
        {
            configureLog( enabled );
        },
        "enabled"_a = true
    );

    py::class_< GLContextView, std::shared_ptr< GLContextView > >( m, "GLContext" )
        .doc() = "Wraps and represents an OpenGL context.";

    py::class_< SpatialView, std::shared_ptr< SpatialView > >( m, "Spatial" )
        .def_property_readonly( "has_parent",
            VIEW_DELEGATE( SpatialView, spatial->hasParent() )
        )
        .def( "detach_from_parent",
            []( SpatialView& self )
            {
                self.ownedBy.reset();
                self.spatial->detachFromParent();
            }
        )
        .def_property( "is_movable",
            VIEW_DELEGATE( SpatialView, spatial->isMovable() ),
            VIEW_DELEGATE( SpatialView, spatial->setMovable( movable ), bool movable )
        )
        .def_property( "tag",
            VIEW_DELEGATE( SpatialView, spatial->tag() ),
            VIEW_DELEGATE( SpatialView, spatial->setTag( tag ), const std::string& tag )
        )
        .def_property( "local_transform",
            VIEW_DELEGATE( SpatialView, spatial->localTransform ),
            VIEW_DELEGATE( SpatialView, spatial->localTransform = localTransform, const LibCarna::base::math::Matrix4f& localTransform )
        )
        .def( "update_world_transform",
            VIEW_DELEGATE( SpatialView, spatial->updateWorldTransform() )
        )
        .def_property_readonly( "world_transform",
            VIEW_DELEGATE( SpatialView, spatial->worldTransform() )
        );

    py::class_< NodeView, std::shared_ptr< NodeView >, SpatialView >( m, "Node" )
        .def( py::init< const std::string& >(), "tag"_a = "" )
        .def( "attach_child", &NodeView::attachChild )
        .def( "children",
            VIEW_DELEGATE( NodeView, node().children() )
        );

    py::class_< CameraView, std::shared_ptr< CameraView >, SpatialView >( m, "Camera" )
        .def( py::init<>() )
        .def_property( "projection",
            VIEW_DELEGATE( CameraView, camera().projection() ),
            VIEW_DELEGATE( CameraView, camera().setProjection( projection ), const LibCarna::base::math::Matrix4f& projection )
        )
        .def_property( "orthogonal_projection_hint",
            VIEW_DELEGATE( CameraView, camera().isOrthogonalProjectionHintSet() ),
            VIEW_DELEGATE( CameraView, camera().setOrthogonalProjectionHint( orthogonalProjectionHint ), bool orthogonalProjectionHint )
        )
        .def_property_readonly( "view_transform",
            VIEW_DELEGATE( CameraView, camera().viewTransform() )
        );

    py::class_< GeometryFeatureView, std::shared_ptr< GeometryFeatureView > >( m, "GeometryFeature" );

    py::class_< GeometryView, std::shared_ptr< GeometryView >, SpatialView >( m, "Geometry" )
        .def( py::init< unsigned int, const std::string& >(), "geometry_type"_a, "tag"_a = "" )
        .def_property_readonly( "geometry_type",
            VIEW_DELEGATE( GeometryView, geometry().geometryType )
        )
        .def_property_readonly( "features_count",
            VIEW_DELEGATE( GeometryView, geometry().featuresCount() )
        )
        .def( "put_feature",
            VIEW_DELEGATE( GeometryView, geometry().putFeature( role, feature.geometryFeature ), unsigned int role, GeometryFeatureView& feature )
        )
        .def( "remove_feature",
            VIEW_DELEGATE( GeometryView, geometry().removeFeature( role ), unsigned int role )
        )
        .def( "remove_feature",
            VIEW_DELEGATE( GeometryView, geometry().removeFeature( feature.geometryFeature ), GeometryFeatureView& feature )
        )
        .def( "clear_features",
            VIEW_DELEGATE( GeometryView, geometry().clearFeatures() )
        )
        .def( "has_feature",
            VIEW_DELEGATE( GeometryView, geometry().hasFeature( role ), unsigned int role )
        )
        .def( "has_feature",
            VIEW_DELEGATE( GeometryView, geometry().hasFeature( feature.geometryFeature ), GeometryFeatureView& feature )
        );

    py::class_< MaterialView, std::shared_ptr< MaterialView >, GeometryFeatureView >( m, "Material" )
        .def( py::init< const std::string& >(), "shader_name"_a )
        .def( "__setitem__", &MaterialView::setParameter< LibCarna::base::math::Vector4f > )
        .def( "__setitem__", &MaterialView::setParameter< LibCarna::base::math::Vector3f > )
        .def( "__setitem__", &MaterialView::setParameter< LibCarna::base::math::Vector2f > )
        .def( "__setitem__", &MaterialView::setParameter< float > )
        .def( "clear_parameters",
            VIEW_DELEGATE( MaterialView, material().clearParameters() )
        )
        .def( "remove_parameter",
            VIEW_DELEGATE( MaterialView, material().removeParameter( name ), const std::string& name )
        )
        .def( "has_parameter",
            VIEW_DELEGATE( MaterialView, material().hasParameter( name ), const std::string& name )
        );

    py::class_< Surface >( m, "Surface" )
        .def( py::init< const GLContextView&, unsigned int, unsigned int >(), "gl_context"_a, "width"_a, "height"_a )
        .def_property_readonly( "width", &Surface::width )
        .def_property_readonly( "height", &Surface::height )
        .def( "begin", &Surface::begin )
        .def( "end", &Surface::end );
    
    py::class_< RenderStageView, std::shared_ptr< RenderStageView > >( m, "RenderStage" )
        .def_property( "enabled",
            VIEW_DELEGATE( RenderStageView, renderStage->isEnabled() ),
            VIEW_DELEGATE( RenderStageView, renderStage->setEnabled( enabled ), bool enabled )
        )
        .def_property_readonly( "renderer",
            VIEW_DELEGATE( RenderStageView, ownedBy.get() )
        );

    py::class_< MeshRenderingStageView, std::shared_ptr< MeshRenderingStageView >, RenderStageView >( m, "MeshRenderingStage" )
        .def_readonly_static( "ROLE_DEFAULT_MESH", &MeshRenderingStageView::ROLE_DEFAULT_MESH )
        .def_readonly_static( "ROLE_DEFAULT_MATERIAL", &MeshRenderingStageView::ROLE_DEFAULT_MATERIAL );

    py::class_< FrameRendererView, std::shared_ptr< FrameRendererView > >( m, "FrameRenderer" )
        .def( py::init< GLContextView&, unsigned int, unsigned int, bool >(),
            "gl_context"_a, "width"_a, "height"_a, "fit_square"_a = false
        )
        .def( "append_stage",
            &FrameRendererView::appendStage,
            "stage"_a
        )
        .def_property_readonly( "gl_context",
            VIEW_DELEGATE( FrameRendererView, context.get() )
        )
        .def_property_readonly( "width",
            VIEW_DELEGATE( FrameRendererView, frameRenderer.width() )
        )
        .def_property_readonly( "height",
            VIEW_DELEGATE( FrameRendererView, frameRenderer.height() )
        )
        .def( "set_background_color",
            VIEW_DELEGATE( FrameRendererView, frameRenderer.setBackgroundColor( color ), const LibCarna::base::Color& color ),
            "color"_a
        )
        .def( "reshape",
            VIEW_DELEGATE( FrameRendererView,
                frameRenderer.reshape( width, height ),
                unsigned int width, unsigned int height
            ),
            "width"_a, "height"_a
        )
        .def( "reshape",
            VIEW_DELEGATE( FrameRendererView,
                frameRenderer.reshape( width, height, fitSquare ),
                unsigned int width, unsigned int height, bool fitSquare
            ),
            "width"_a, "height"_a, "fit_square"_a = false
        )
        .def( "render",
            []( FrameRendererView& self, CameraView& camera, NodeView* root ) {
                if( root == nullptr )
                {
                    self.frameRenderer.render( camera.camera() );
                }
                else
                {
                    self.frameRenderer.render( camera.camera(), root->node() );
                }
            },
            "camera"_a, "root"_a = nullptr
        );

    m.def_submodule( "MeshFactory" )
        .def( "create_box",
            []( float width, float height, float depth )
            {
                return new GeometryFeatureView( LibCarna::base::MeshFactory< LibCarna::base::PNVertex >::createBox( width, height, depth ) );
            },
            "width"_a, "height"_a, "depth"_a
        )
        .def( "create_ball",
            []( float radius, unsigned int degree )
            {
                return new GeometryFeatureView( LibCarna::base::MeshFactory< LibCarna::base::PNVertex >::createBall( radius, degree ) );
            },
            "radius"_a, "degree"_a=4
        )
        .def( "create_point",
            []()
            {
                return new GeometryFeatureView( LibCarna::base::MeshFactory< LibCarna::base::PVertex >::createPoint() );
            }
        );

    m.def_submodule( "math" )
        .def( "ortho", &LibCarna::base::math::ortho4f, "left"_a, "right"_a, "bottom"_a, "top"_a, "z_near"_a, "z_far"_a )
        .def( "frustum",
            py::overload_cast< float, float, float, float, float, float >( &LibCarna::base::math::frustum4f ),
            "left"_a, "right"_a, "bottom"_a, "top"_a, "z_near"_a, "z_far"_a
        )
        .def( "frustum",
            py::overload_cast< float, float, float, float >( &LibCarna::base::math::frustum4f ),
            "fov"_a, "height_over_width"_a, "z_near"_a, "z_far"_a
        )
        .def( "deg2rad", &LibCarna::base::math::deg2rad, "degrees"_a )
        .def( "rad2deg", &LibCarna::base::math::rad2deg, "radians"_a )
        .def( "rotation", &LibCarna::base::math::rotation4f< LibCarna::base::math::Vector3f >, "axis"_a, "radians"_a )
        .def( "translation", &LibCarna::base::math::translation4f< LibCarna::base::math::Vector3f >, "offset"_a )
        .def( "translation",
            static_cast< LibCarna::base::math::Matrix4f( * )( float, float, float ) >( &LibCarna::base::math::translation4f ),
            "tx"_a, "ty"_a, "tz"_a
        )
        .def( "scaling", &LibCarna::base::math::scaling4f< float >, "factors"_a )
        .def( "scaling",
            static_cast< LibCarna::base::math::Matrix4f( * )( float, float, float ) >( &LibCarna::base::math::scaling4f ),
            "sx"_a, "sy"_a, "sz"_a )
        .def( "scaling", static_cast< LibCarna::base::math::Matrix4f( * )( float ) >( &LibCarna::base::math::scaling4f ), "uniform_factor"_a )
        .def( "plane",
            []( const LibCarna::base::math::Vector3f& normal, float distance )
            {
                return LibCarna::base::math::plane4f( normal.normalized(), distance );
            },
            "normal"_a, "distance"_a
        )
        .def( "plane",
            []( const LibCarna::base::math::Vector3f& normal, const LibCarna::base::math::Vector3f& support )
            {
                return LibCarna::base::math::plane4f( normal.normalized(), support );
            },
            "normal"_a, "support"_a 
        );

    py::class_< LibCarna::base::Color >( m, "Color" )
        .def_readonly_static( "WHITE", &LibCarna::base::Color::WHITE )
        .def_readonly_static( "WHITE_NO_ALPHA", &LibCarna::base::Color::WHITE_NO_ALPHA )
        .def_readonly_static( "BLACK", &LibCarna::base::Color::BLACK )
        .def_readonly_static( "BLACK_NO_ALPHA", &LibCarna::base::Color::BLACK_NO_ALPHA )
        .def_readonly_static( "RED", &LibCarna::base::Color::RED )
        .def_readonly_static( "RED_NO_ALPHA", &LibCarna::base::Color::RED_NO_ALPHA )
        .def_readonly_static( "GREEN", &LibCarna::base::Color::GREEN )
        .def_readonly_static( "GREEN_NO_ALPHA", &LibCarna::base::Color::GREEN_NO_ALPHA )
        .def_readonly_static( "BLUE", &LibCarna::base::Color::BLUE )
        .def_readonly_static( "BLUE_NO_ALPHA", &LibCarna::base::Color::BLUE_NO_ALPHA )
        .def( py::init< unsigned char, unsigned char, unsigned char, unsigned char >(), "r"_a, "g"_a, "b"_a, "a"_a )
        .def( py::init< const LibCarna::base::math::Vector4f& >(), "rgba"_a )
        .def( py::init<>() )
        .def_readwrite( "r", &LibCarna::base::Color::r )
        .def_readwrite( "g", &LibCarna::base::Color::g )
        .def_readwrite( "b", &LibCarna::base::Color::b )
        .def_readwrite( "a", &LibCarna::base::Color::a )
        .def(
            "__eq__",
            []( LibCarna::base::Color& self, LibCarna::base::Color& other )
            {
                return self == other;
            }
        )
        .def(
            "toarray",
            []( LibCarna::base::Color& self )
            {
                return static_cast< const LibCarna::base::math::Vector4f& >( self );
            }
        );

    py::class_< ColorMapView, std::shared_ptr< ColorMapView > >( m, "ColorMap" )
        .def( "clear",
            VIEW_DELEGATE( ColorMapView, colorMap.clear() )
        )
        .def( "write_linear_segment",
            VIEW_DELEGATE_RETURN_SELF
                ( const std::shared_ptr< ColorMapView >
                , get()->colorMap.writeLinearSegment( intensityFirst, intensityLast, colorFirst, colorLast )
                , float intensityFirst
                , float intensityLast
                , const LibCarna::base::Color& colorFirst
                , const LibCarna::base::Color& colorLast ),
            "intensity_first"_a, "intensity_last"_a, "color_first"_a, "color_last"_a
        )
        .def( "write_linear_spline",
            VIEW_DELEGATE_RETURN_SELF
                ( const std::shared_ptr< ColorMapView >
                , get()->colorMap.writeLinearSpline( colors )
                , const std::vector< LibCarna::base::Color >& colors ),
            "colors"_a
        )
        .def_property_readonly(
            "color_list",
            VIEW_DELEGATE( ColorMapView, colorMap.getColorList() )
        );

/*
    py::class_< BlendFunction >( m, "BlendFunction" )
        .def( py::init< int, int >() )
        .def_readonly( "source_factor", &BlendFunction::sourceFactor )
        .def_readonly( "destination_factor", &BlendFunction::destinationFactor );
*/

}