#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

#if CARNA_EXTRA_CHECKS
#include <pybind11/stl.h>
#endif // CARNA_EXTRA_CHECKS

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/FrameRenderer.h>
#include <Carna/base/Node.h>
#include <Carna/base/Camera.h>
#include <Carna/base/Geometry.h>
#include <Carna/base/GeometryFeature.h>
#include <Carna/base/Color.h>
#include <Carna/base/Material.h>
#include <Carna/base/BoundingVolume.h>
#include <Carna/base/GLContext.h>
#include <Carna/base/MeshFactory.h>
#include <Carna/base/ManagedMesh.h>
#include <Carna/base/RenderStage.h>
#include <Carna/base/BlendFunction.h>
#include <Carna/py/py.h>
#include "Surface.cpp"

using namespace Carna::base;
using namespace Carna::py;



/*
py::array_t< unsigned char > Surface__end( const Surface& surface )
{
    const unsigned char* pixelData = surface.end();
    py::buffer_info buf; // performs flipping
    buf.itemsize = sizeof( unsigned char );
    buf.format   = py::format_descriptor< unsigned char >::value;
    buf.ndim     = 3;
    buf.shape    = { surface.height(), surface.width(), 3 };
    buf.strides  = { -buf.itemsize * 3 * surface.width(), buf.itemsize * 3, buf.itemsize };
    buf.ptr      = const_cast< unsigned char* >( pixelData ) + buf.itemsize * 3 * surface.width() * (surface.height() - 1);
    return py::array( buf );
}

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
    Spatial* const spatial;

    explicit SpatialView( Spatial* spatial );

    virtual ~SpatialView();

}; // SpatialView


SpatialView::SpatialView( Spatial* spatial )
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
        if( Node* const node = dynamic_cast< Node* >( spatial ) )
        {
            node->visitChildren(
                true,
                []( Spatial& child )
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

class NodeView : public SpatialView
{

public:

    template< typename... Args >
    explicit NodeView( Args... args );

    Node& node();

    void attachChild( SpatialView& child );

}; // NodeView


template< typename... Args >
NodeView::NodeView( Args... args )
    : SpatialView::SpatialView( new Node( args... ) )
{
}


Node& NodeView::node()
{
    return static_cast< Node& >( *spatial );
}


void NodeView::attachChild( SpatialView& child )
{
    /* Verify that the child is not already attached to another parent.
     */
    CARNA_ASSERT_EX( !child.spatial->hasParent(), "Child already has a parent." );

    /* Check for circular relations (verify that `this` is not a child of `child`).
     */
    bool circular = false;
    if( Node* const childNode = dynamic_cast< Node* >( child.spatial ) )
    {
        childNode->visitChildren(
            true,
            [ &circular, this ]( const Spatial& spatial )
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

class CameraView : public SpatialView
{

public:

    template< typename... Args >
    explicit CameraView( Args... args );

    Camera& camera();

}; // CameraView


template< typename... Args >
CameraView::CameraView( Args... args )
    : SpatialView::SpatialView( new Camera( args... ) )
{
}


Camera& CameraView::camera()
{
    return static_cast< Camera& >( *spatial );
}



// ----------------------------------------------------------------------------------
// GeometryView
// ----------------------------------------------------------------------------------

class GeometryView : public SpatialView
{

public:

    template< typename... Args >
    explicit GeometryView( Args... args );

    Geometry& geometry();

}; // GeometryView


template< typename... Args >
GeometryView::GeometryView( Args... args )
    : SpatialView::SpatialView( new Geometry( args... ) )
{
}


Geometry& GeometryView::geometry()
{
    return static_cast< Geometry& >( *spatial );
}



// ----------------------------------------------------------------------------------
// GeometryFeatureView
// ----------------------------------------------------------------------------------

class GeometryFeatureView : public std::enable_shared_from_this< GeometryFeatureView >
{
public:

    /* The geometry feature of this view.
     */
    GeometryFeature& geometryFeature;

    explicit GeometryFeatureView( GeometryFeature& geometryFeature );

    virtual ~GeometryFeatureView();

}; // GeometryFeatureView


GeometryFeatureView::GeometryFeatureView( GeometryFeature& geometryFeature )
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

class MaterialView : public GeometryFeatureView
{
public:

    template< typename... Args >
    explicit MaterialView( Args... args );

    Material& material();

    template< typename ParameterType >
    void setParameter( const std::string& name, const ParameterType& value );

}; // MaterialView


template< typename... Args >
MaterialView::MaterialView( Args... args )
    : GeometryFeatureView::GeometryFeatureView( Material::create( args... ) )
{
}


Material& MaterialView::material()
{
    return static_cast< Material& >( geometryFeature );
}


template< typename ParameterType >
void MaterialView::setParameter( const std::string& name, const ParameterType& value )
{
    material().setParameter( name, value );
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: base
// ----------------------------------------------------------------------------------

#define VIEW_DELEGATE( ViewType, delegate, ... ) \
    []( ViewType& self __VA_OPT__( , __VA_ARGS__ ) ) \
    { \
        return self.delegate; \
    }


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

    py::class_< Carna::base::GLContext >( m, "GLContext" );

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
            VIEW_DELEGATE( SpatialView, spatial->localTransform = localTransform, const math::Matrix4f& localTransform )
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
            VIEW_DELEGATE( CameraView, camera().setProjection( projection ), const math::Matrix4f& projection )
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
        .def( "__setitem__", &MaterialView::setParameter< math::Vector4f > )
        .def( "__setitem__", &MaterialView::setParameter< math::Vector3f > )
        .def( "__setitem__", &MaterialView::setParameter< math::Vector2f > )
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

/*
    py::class_< Surface >( m, "Surface" )
        .def_static( "create", []( const GLContext& glContext, unsigned int width, unsigned int height )
        {
            return new Surface( glContext, width, height );
        }
        , py::return_value_policy::reference, "glContext"_a, "width"_a, "height"_a )
        .def_property_readonly( "width", &Surface::width )
        .def_property_readonly( "height", &Surface::height )
        .def_property_readonly( "gl_context", []( const Surface& self )
        {
            return &self.glContext;
        }
        , py::return_value_policy::reference )
        .def( "begin", &Surface::begin )
        .def( "end", &Surface__end )
        .DEF_FREE( Surface );

    py::class_< RenderStage >( m, "RenderStage" )
        .def_property( "enabled", &RenderStage::isEnabled, &RenderStage::setEnabled )
        .def_property_readonly( "renderer", py::overload_cast<>( &RenderStage::renderer, py::const_ ) )
        .DEF_FREE( RenderStage );

    py::class_< RenderStageSequence >( m, "RenderStageSequence" )
        .def_property_readonly( "stages", &RenderStageSequence::stages )
        .def( "append_stage", &RenderStageSequence::appendStage )
        .def( "clear_stages", &RenderStageSequence::clearStages )
        .def( "stage_at", &RenderStageSequence::stageAt );

    py::class_< FrameRenderer, RenderStageSequence >( m, "FrameRenderer" )
        .def_static( "create", []( GLContext& glContext, unsigned int width, unsigned int height, bool fitSquare )
        {
            return new FrameRenderer( glContext, width, height, fitSquare );
        }
        , py::return_value_policy::reference, "glContext"_a, "width"_a, "height"_a, "fitSquare"_a = false )
        .def_property_readonly( "gl_context", &FrameRenderer::glContext )
        .def_property_readonly( "width", &FrameRenderer::width )
        .def_property_readonly( "height", &FrameRenderer::height )
        .def( "set_background_color", &FrameRenderer::setBackgroundColor )
        .def( "reshape", py::overload_cast< unsigned int, unsigned int >( &FrameRenderer::reshape ) )
        .def( "set_fit_square", []( FrameRenderer* self, bool fitSquare )
        {
            self->reshape( self->width(), self->height(), fitSquare );
        }, "fitSquare"_a )
        .def( "render", []( FrameRenderer* self, Camera& cam, Node* root ){
            if( root == nullptr ) self->render( cam );
            else self->render( cam, *root );
        }, "cam"_a, "root"_a = nullptr )
        .DEF_FREE( FrameRenderer );

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
