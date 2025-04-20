#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/FrameRenderer.h>
#include <Carna/base/Node.h>
#include <Carna/base/Camera.h>
#include <Carna/base/Geometry.h>
#include <Carna/base/GeometryFeature.h>
#include <Carna/base/Color.h>
#include <Carna/base/BoundingVolume.h>
#include <Carna/base/GLContext.h>
//#include <Carna/base/MeshFactory.h>
//#include <Carna/base/ManagedMesh.h>
#include <Carna/base/RenderStage.h>
//#include <Carna/base/BlendFunction.h>
#include <Carna/helpers/FrameRendererHelper.h>
#include <Carna/py/base.h>
#include <Carna/py/Surface.h>

using namespace Carna::py;
using namespace Carna::py::base;



/*
template< typename VectorElementType , int dimension >
Eigen::Matrix< float, dimension, 1 > normalized( const Eigen::Matrix< VectorElementType, dimension, 1 >& vector )
{
    const float length = std::sqrt( static_cast< float >( math::length2( vector ) ) );
    if( length > 0 ) return vector / length;
    else return vector;
}

math::Matrix4f math__plane4f_by_distance( const math::Vector3f& normal, float distance )
{
    return math::plane4f( normalized( normal ), distance );
}

math::Matrix4f math__plane4f_by_support( const math::Vector3f& normal, const math::Vector3f& support )
{
    return math::plane4f( normalized( normal ), support );
}
*/



// ----------------------------------------------------------------------------------
// debugEvents
// ----------------------------------------------------------------------------------

#if CARNA_EXTRA_CHECKS

static std::vector< std::string > debugEvents;


template< typename SourceType >
static void debugEvent( SourceType* self, const std::string& event )
{
    std::stringstream ss;
    ss << self << ": " << event;
    debugEvents.push_back( ss.str() );
}

#endif // CARNA_EXTRA_CHECKS



// ----------------------------------------------------------------------------------
// GLContextView
// ----------------------------------------------------------------------------------

GLContextView::GLContextView( Carna::base::GLContext* context )
    : context( context )
{
    #if CARNA_EXTRA_CHECKS
    debugEvent( context, "created" );
    #endif // CARNA_EXTRA_CHECKS
}


GLContextView::~GLContextView()
{
    #if CARNA_EXTRA_CHECKS
    debugEvent( context, "deleted" );
    #endif // CARNA_EXTRA_CHECKS
}



// ----------------------------------------------------------------------------------
// SpatialView
// ----------------------------------------------------------------------------------

SpatialView::SpatialView( Carna::base::Spatial* spatial )
    : ownedBy( nullptr )
    , spatial( spatial )
{
    #if CARNA_EXTRA_CHECKS
    debugEvent( spatial, "created" );
    #endif // CARNA_EXTRA_CHECKS
}


SpatialView::~SpatialView()
{
    if( ownedBy.get() == nullptr )
    {
        #if CARNA_EXTRA_CHECKS
        if( Carna::base::Node* const node = dynamic_cast< Carna::base::Node* >( spatial ) )
        {
            node->visitChildren(
                true,
                []( Carna::base::Spatial& child )
                {
                    debugEvent( &child, "deleted" );
                }
            );
        }
        debugEvent( spatial, "deleted" );
        #endif // CARNA_EXTRA_CHECKS

        /* The spatial object of this view is not owned by any other spatial object,
         * thus it is safe to delete the object, when the last reference dies.
         */
         delete spatial;
    }
}



// ----------------------------------------------------------------------------------
// NodeView
// ----------------------------------------------------------------------------------

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
    #if CARNA_EXTRA_CHECKS
    debugEvent( renderStage, "created" );
    #endif // CARNA_EXTRA_CHECKS
}


RenderStageView::~RenderStageView()
{
    if( ownedBy.get() == nullptr )
    {
        #if CARNA_EXTRA_CHECKS
        debugEvent( renderStage, "deleted" );
        #endif // CARNA_EXTRA_CHECKS

        /* The render stage of this view is not owned by any \a FrameRendererView,
         * thus it is safe to delete the object, when the last reference dies.
         */
         delete renderStage;
    }
}



// ----------------------------------------------------------------------------------
// FrameRendererView
// ----------------------------------------------------------------------------------

FrameRendererView::FrameRendererView
        ( GLContextView& context
        , const std::vector< RenderStageView* >& renderStages
        , unsigned int width
        , unsigned int height
        , bool fitSquare)
    : context( context.shared_from_this() )
    , frameRenderer( *( context.context ), width, height, fitSquare )
{
    /* Verify that the render stages are not already added to another frame renderer.
     */
    for( RenderStageView* renderStage : renderStages )
    {
        CARNA_ASSERT_EX( renderStage->ownedBy.get() == nullptr, "Render stage was already added to a frame renderer." );
    }

    /* Add the render stages to the frame renderer.
     */
    Carna::helpers::FrameRendererHelper< > frameRendererHelper( frameRenderer );
    for( RenderStageView* renderStage : renderStages )
    {
        renderStage->ownedBy = this->shared_from_this();
        frameRendererHelper << renderStage->renderStage;
    }
    frameRendererHelper.commit();
}


FrameRendererView::~FrameRendererView()
{
    #if CARNA_EXTRA_CHECKS
    for( std::size_it stageIdx = 0; stageIndex < frameRenderer.stages(); ++stageIndex )
    {
        RenderStage* const renderStage = frameRenderer.stageAt( stageIndex );
        debugEvent( renderStage, "deleted" );
    }
    #endif // CARNA_EXTRA_CHECKS
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: base
// ----------------------------------------------------------------------------------

#define VIEW_DELEGATE( ViewType, delegate, ... ) \
    []( ViewType& self __VA_OPT__( , __VA_ARGS__ ) ) \
    { \
        return self.delegate; \
    }


#ifdef BUILD_BASE_MODULE
PYBIND11_MODULE( base, m )
{

    //py::register_exception< AssertionFailure >( m, "AssertionFailure" );  // error: 'const class Carna::base::AssertionFailure' has no member named 'what'

    #if CARNA_EXTRA_CHECKS
    m.def( "debug_events", []()->std::vector< std::string >
        {
            auto debugEvents0 = debugEvents;
            debugEvents.clear();
            return debugEvents0;
        }
    );
    #endif // CARNA_EXTRA_CHECKS

    py::class_< GLContextView, std::shared_ptr< GLContextView > >( m, "GLContext" );

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

    py::class_< FrameRendererView, std::shared_ptr< FrameRendererView > >( m, "FrameRenderer" )
        .def( py::init< GLContextView&, const std::vector< RenderStageView* >&,
            unsigned int, unsigned int, bool >(), "gl_context"_a, "render_stages"_a, "width"_a, "height"_a, "fit_square"_a = false
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

/*
    py::class_< BlendFunction >( m, "BlendFunction" )
        .def( py::init< int, int >() )
        .def_readonly( "source_factor", &BlendFunction::sourceFactor )
        .def_readonly( "destination_factor", &BlendFunction::destinationFactor );

    m.def( "create_box", []( float width, float height, float depth )
    {
        return static_cast< GeometryFeature* >( &MeshFactory< PNVertex >::createBox( width, height, depth ) );
    }
    , py::return_value_policy::reference, "width"_a, "height"_a, "depth"_a );

    m.def( "create_point", []()
    {
        return static_cast< GeometryFeature* >( &MeshFactory< PVertex >::createPoint() );
    }
    , py::return_value_policy::reference );

    m.def( "create_ball", []( float radius, unsigned int degree )
    {
        return static_cast< GeometryFeature* >( &MeshFactory< PNVertex >::createBall( radius, degree ) );
    }
    , py::return_value_policy::reference, "radius"_a, "degree"_a = 3 );

    py::module math = m.def_submodule( "math" );
    math.def( "ortho4f", &math::ortho4f );
    math.def( "frustum4f", py::overload_cast< float, float, float, float >( &math::frustum4f ) );
    math.def( "deg2rad", &math::deg2rad );
    math.def( "rotation4f", static_cast< math::Matrix4f( * )( const math::Vector3f&, float ) >( &math::rotation4f ) );
    math.def( "translation4f", static_cast< math::Matrix4f( * )( float, float, float ) >( &math::translation4f ) );
    math.def( "scaling4f", static_cast< math::Matrix4f( * )( float, float, float ) >( &math::scaling4f ) );
    math.def( "plane4f", math__plane4f_by_distance );
    math.def( "plane4f", math__plane4f_by_support );
*/

}
#endif // BUILD_base_MODULE