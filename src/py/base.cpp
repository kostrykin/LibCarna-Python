#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/FrameRenderer.h>
#include <Carna/base/Camera.h>
#include <Carna/base/Geometry.h>
#include <Carna/base/GeometryFeature.h>
#include <Carna/base/Color.h>
#include <Carna/base/BoundingVolume.h>
#include <Carna/base/GLContext.h>
#include <Carna/base/MeshFactory.h>
#include <Carna/base/RenderStage.h>
//#include <Carna/base/BlendFunction.h>
#include <Carna/base/MeshRenderingStage.h>
#include <Carna/py/base.h>
#include <Carna/py/Surface.h>
#include <Carna/py/Log.h>

using namespace Carna::py;
using namespace Carna::py::base;



// ----------------------------------------------------------------------------------
// GLContextView
// ----------------------------------------------------------------------------------

GLContextView::GLContextView( Carna::base::GLContext* context )
    : context( context )
{
}


GLContextView::~GLContextView()
{
}



// ----------------------------------------------------------------------------------
// SpatialView
// ----------------------------------------------------------------------------------

SpatialView::SpatialView( Carna::base::Spatial* spatial )
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

NodeView::NodeView( Carna::base::Node* node )
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


Carna::base::Node& NodeView::node()
{
    return static_cast< Carna::base::Node& >( *spatial );
}


void NodeView::attachChild( SpatialView& child )
{
    /* Verify that the child is not already attached to another parent.
     */
    CARNA_ASSERT_EX( !child.spatial->hasParent(), "Child already has a parent." );

    /* Check for circular relations (verify that `this` is not a child of `child`).
     */
    bool circular = false;
    if( Carna::base::Node* const childNode = dynamic_cast< Carna::base::Node* >( child.spatial ) )
    {
        childNode->visitChildren(
            true,
            [ &circular, this ]( const Carna::base::Spatial& spatial )
            {
                if( &spatial == this->spatial )
                {
                    circular = true;
                }
            }
        );
    }
    CARNA_ASSERT_EX( !circular, "Circular relations are forbidden." );

    /* Update scene graph structure.
     */
    child.ownedBy = this->shared_from_this();
    this->node().attachChild( child.spatial );
}



// ----------------------------------------------------------------------------------
// CameraView
// ----------------------------------------------------------------------------------

Carna::base::Camera& CameraView::camera()
{
    return static_cast< Carna::base::Camera& >( *spatial );
}



// ----------------------------------------------------------------------------------
// GeometryView
// ----------------------------------------------------------------------------------

Carna::base::Geometry& GeometryView::geometry()
{
    return static_cast< Carna::base::Geometry& >( *spatial );
}



// ----------------------------------------------------------------------------------
// GeometryFeatureView
// ----------------------------------------------------------------------------------

GeometryFeatureView::GeometryFeatureView( Carna::base::GeometryFeature& geometryFeature )
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

Carna::base::Material& MaterialView::material()
{
    return static_cast< Carna::base::Material& >( geometryFeature );
}



// ----------------------------------------------------------------------------------
// RenderStageView
// ----------------------------------------------------------------------------------

RenderStageView::RenderStageView( Carna::base::RenderStage* renderStage )
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

const unsigned int MeshRenderingStageView::ROLE_DEFAULT_MESH = Carna::base::MeshRenderingStageBase::ROLE_DEFAULT_MESH;
const unsigned int MeshRenderingStageView::ROLE_DEFAULT_MATERIAL = Carna::base::MeshRenderingStageBase::ROLE_DEFAULT_MATERIAL;


MeshRenderingStageView::MeshRenderingStageView( Carna::base::RenderStage* renderStage )
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
    CARNA_ASSERT_EX( rsView->ownedBy.get() == nullptr, "Render stage was already added to a frame renderer." );

    /* Add the render stage to the frame renderer (and take ownership).
     */
    rsView->ownedBy = this->shared_from_this();
    frameRenderer.appendStage( rsView->renderStage );
}


FrameRendererView::~FrameRendererView()
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
        Carna::base::Log::instance().setWriter( new Carna::base::Log::StdWriter() );
    }
    else
    {
        Carna::base::Log::instance().setWriter( new NullWriter() );
    }
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: base
// ----------------------------------------------------------------------------------

PYBIND11_MODULE( base, m )
{

    //py::register_exception< AssertionFailure >( m, "AssertionFailure" );  // error: 'const class Carna::base::AssertionFailure' has no member named 'what'

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
            VIEW_DELEGATE( SpatialView, spatial->localTransform = localTransform, const Carna::base::math::Matrix4f& localTransform )
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
            VIEW_DELEGATE( CameraView, camera().setProjection( projection ), const Carna::base::math::Matrix4f& projection )
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
        .def( "__setitem__", &MaterialView::setParameter< Carna::base::math::Vector4f > )
        .def( "__setitem__", &MaterialView::setParameter< Carna::base::math::Vector3f > )
        .def( "__setitem__", &MaterialView::setParameter< Carna::base::math::Vector2f > )
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
            VIEW_DELEGATE( FrameRendererView, frameRenderer.setBackgroundColor( color ), const Carna::base::Color& color ),
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
                return new GeometryFeatureView( Carna::base::MeshFactory< Carna::base::PNVertex >::createBox( width, height, depth ) );
            },
            "width"_a, "height"_a, "depth"_a
        )
        .def( "create_ball",
            []( float radius, unsigned int degree )
            {
                return new GeometryFeatureView( Carna::base::MeshFactory< Carna::base::PNVertex >::createBall( radius, degree ) );
            },
            "radius"_a, "degree"_a=3
        )
        .def( "create_point",
            []()
            {
                return new GeometryFeatureView( Carna::base::MeshFactory< Carna::base::PVertex >::createPoint() );
            }
        );

    m.def_submodule( "math" )
        .def( "ortho", &Carna::base::math::ortho4f, "left"_a, "right"_a, "bottom"_a, "top"_a, "z_near"_a, "z_far"_a )
        .def( "frustum",
            py::overload_cast< float, float, float, float, float, float >( &Carna::base::math::frustum4f ),
            "left"_a, "right"_a, "bottom"_a, "top"_a, "z_near"_a, "z_far"_a
        )
        .def( "frustum",
            py::overload_cast< float, float, float, float >( &Carna::base::math::frustum4f ),
            "fov"_a, "height_over_width"_a, "z_near"_a, "z_far"_a
        )
        .def( "deg2rad", &Carna::base::math::deg2rad, "degrees"_a )
        .def( "rad2deg", &Carna::base::math::rad2deg, "radians"_a )
        .def( "rotation", &Carna::base::math::rotation4f< Carna::base::math::Vector3f >, "axis"_a, "radians"_a )
        .def( "translation", &Carna::base::math::translation4f< Carna::base::math::Vector3f >, "offset"_a )
        .def( "translation",
            static_cast< Carna::base::math::Matrix4f( * )( float, float, float ) >( &Carna::base::math::translation4f ),
            "tx"_a, "ty"_a, "tz"_a
        )
        .def( "scaling", &Carna::base::math::scaling4f< float >, "factors"_a )
        .def( "scaling",
            static_cast< Carna::base::math::Matrix4f( * )( float, float, float ) >( &Carna::base::math::scaling4f ),
            "sx"_a, "sy"_a, "sz"_a )
        .def( "scaling", static_cast< Carna::base::math::Matrix4f( * )( float ) >( &Carna::base::math::scaling4f ), "uniform_factor"_a )
        .def( "plane",
            []( const Carna::base::math::Vector3f& normal, float distance )
            {
                return Carna::base::math::plane4f( normal.normalized(), distance );
            },
            "normal"_a, "distance"_a
        )
        .def( "plane",
            []( const Carna::base::math::Vector3f& normal, const Carna::base::math::Vector3f& support )
            {
                return Carna::base::math::plane4f( normal.normalized(), support );
            },
            "normal"_a, "support"_a 
        );

    py::class_< Carna::base::Color >( m, "Color" )
        .def_readonly_static( "WHITE", &Carna::base::Color::WHITE )
        .def_readonly_static( "WHITE_NO_ALPHA", &Carna::base::Color::WHITE_NO_ALPHA )
        .def_readonly_static( "BLACK", &Carna::base::Color::BLACK )
        .def_readonly_static( "BLACK_NO_ALPHA", &Carna::base::Color::BLACK_NO_ALPHA )
        .def_readonly_static( "RED", &Carna::base::Color::RED )
        .def_readonly_static( "RED_NO_ALPHA", &Carna::base::Color::RED_NO_ALPHA )
        .def_readonly_static( "GREEN", &Carna::base::Color::GREEN )
        .def_readonly_static( "GREEN_NO_ALPHA", &Carna::base::Color::GREEN_NO_ALPHA )
        .def_readonly_static( "BLUE", &Carna::base::Color::BLUE )
        .def_readonly_static( "BLUE_NO_ALPHA", &Carna::base::Color::BLUE_NO_ALPHA )
        .def( py::init< unsigned char, unsigned char, unsigned char, unsigned char >(), "r"_a, "g"_a, "b"_a, "a"_a )
        .def( py::init< const Carna::base::math::Vector4f& >(), "rgba"_a )
        .def( py::init<>() )
        .def_readwrite( "r", &Carna::base::Color::r )
        .def_readwrite( "g", &Carna::base::Color::g )
        .def_readwrite( "b", &Carna::base::Color::b )
        .def_readwrite( "a", &Carna::base::Color::a )
        .def(
            "__eq__",
            []( Carna::base::Color& self, Carna::base::Color& other )
            {
                return self == other;
            }
        )
        .def(
            "toarray",
            []( Carna::base::Color& self )
            {
                return static_cast< const Carna::base::math::Vector4f& >( self );
            }
        );

/*
    py::class_< BlendFunction >( m, "BlendFunction" )
        .def( py::init< int, int >() )
        .def_readonly( "source_factor", &BlendFunction::sourceFactor )
        .def_readonly( "destination_factor", &BlendFunction::destinationFactor );
*/

}