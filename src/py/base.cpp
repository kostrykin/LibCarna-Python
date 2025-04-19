#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>  // TODO: only for debug

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

#if CARNA_EXRA_CHECKS

static std::vector< std::string > debugEvents;


template< typename SourceType >
static void debugEvent( SourceType* self, const std::string& event )
{
    std::stringstream ss;
    ss << self << ": " << event;
    debugEvents.push_back( ss.str() );
}

#endif // CARNA_EXRA_CHECKS



// ----------------------------------------------------------------------------------
// SpatialView
// ----------------------------------------------------------------------------------

template< typename SpatialType >
class SpatialView : public std::enable_shared_from_this< SpatialView< SpatialType > >
{

public:

    /* The object that owns the spatial object of this view. The spatial object of
     * this view is owned by the view, if it is not owned by any other spatial object.
     */
    std::shared_ptr< SpatialView< Node > > ownedBy;

    /* The spatial object of this view.
     */
    SpatialType* const spatial;

    template< typename... Args >
    SpatialView( Args... args );

    ~SpatialView();

}; // SpatialView< SpatialType >


template< typename SpatialType >
template< typename... Args >
SpatialView< SpatialType >::SpatialView( Args... args )
    : ownedBy( nullptr )
    , spatial( new SpatialType( args... ) )
{
    #if CARNA_EXRA_CHECKS
    debugEvent( spatial, "created" );
    #endif // CARNA_EXRA_CHECKS
}


template< typename SpatialType >
SpatialView< SpatialType >::~SpatialView()
{
    if( ownedBy.get() == nullptr )
    {
        #if CARNA_EXRA_CHECKS
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
        #endif // CARNA_EXRA_CHECKS

        /* The spatial object of this view is not owned by any other spatial object,
         * thus it is safe to delete the object, when the last reference dies.
         */
         delete spatial;
    }
}


template< typename SpatialType >
void attachChild( SpatialView< Node >& self, SpatialView< SpatialType >& child )
{
    /* Verify that the child is not already attached to another parent.
     */
    CARNA_ASSERT_EX( !child.spatial->hasParent(), "Child already has a parent." );

    /* Check for circular relations (verify that `self` is not a child of `child`).
     */
    bool circular = false;
    if( Node* const childNode = dynamic_cast< Node* >( child.spatial ) )
    {
        childNode->visitChildren(
            true,
            [ &circular, &self ]( const Spatial& spatial )
            {
                if( &spatial == self.spatial )
                {
                    circular = true;
                }
            }
        );
    }
    CARNA_ASSERT_EX( !circular, "Circular relations are forbidden." );

    /* Update scene graph structure.
     */
    child.ownedBy = self.shared_from_this();
    self.spatial->attachChild( child.spatial );
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: base
// ----------------------------------------------------------------------------------

template< typename SpatialType, typename ClassType >
ClassType& addInterface_Spatial( ClassType& cls )
{
    cls.def_property_readonly( "has_parent",
        []( SpatialView< SpatialType >& self )->bool
        {
            return self.spatial->hasParent();
        }
    );
    cls.def( "detach_from_parent",
        []( SpatialView< SpatialType >& self )
        {
            self.ownedBy.reset();
            self.spatial->detachFromParent();
        }
    );
    cls.def_property( "is_movable",
        []( SpatialView< SpatialType >& self )->bool
        {
            return self.spatial->isMovable();
        },
        []( SpatialView< SpatialType >& self, bool movable )
        {
            self.spatial->setMovable( movable );
        }
    );
    cls.def_property( "tag",
        []( SpatialView< SpatialType >& self )->const std::string&
        {
            return self.spatial->tag();
        },
        []( SpatialView< SpatialType >& self, const std::string& tag )
        {
            self.spatial->setTag( tag );
        }
    );
    cls.def_property( "local_transform",
        []( SpatialView< SpatialType >& self )->const math::Matrix4f&
        {
            return self.spatial->localTransform;
        },
        []( SpatialView< SpatialType >& self, const math::Matrix4f& localTransform )
        {
            self.spatial->localTransform = localTransform;
        }
    );
    cls.def( "update_world_transform",
        []( SpatialView< SpatialType >& self )
        {
            self.spatial->updateWorldTransform();
        }
    );
    cls.def_property_readonly( "world_transform",
        []( SpatialView< SpatialType >& self )->const math::Matrix4f&
        {
            return self.spatial->worldTransform();
        }
    );
    return cls;
}


PYBIND11_MODULE( base, m )
{

    //py::register_exception< AssertionFailure >( m, "AssertionFailure" );  // error: 'const class Carna::base::AssertionFailure' has no member named 'what'

    #if CARNA_EXRA_CHECKS
    m.def( "debug_events", []()->std::vector< std::string >
        {
            auto debugEvents0 = debugEvents;
            debugEvents.clear();
            return debugEvents0;
        }
    );
    #endif // CARNA_EXRA_CHECKS

    py::class_< Carna::base::GLContext >( m, "GLContext" );

    auto _Node = py::class_< SpatialView< Node >, std::shared_ptr< SpatialView< Node > > >( m, "Node" );
    addInterface_Spatial< Node >( _Node )
        .def( py::init< const std::string& >(), "tag"_a = "" )
        .def( "attach_child", &attachChild< Node > )
        .def( "attach_child", &attachChild< Camera > )
        .def( "attach_child", &attachChild< Geometry > )
        .def( "children", []( SpatialView< Node >& self )->int
            {
                return self.spatial->children();
            }
        );

    auto _Camera = py::class_< SpatialView< Camera >, std::shared_ptr< SpatialView< Camera > > >( m, "Camera" );
    addInterface_Spatial< Camera >( _Camera )
        .def( py::init<>() )
        .def_property( "projection",
            []( SpatialView< Camera >& self )->const math::Matrix4f&
            {
                return self.spatial->projection();
            },
            []( SpatialView< Camera >& self, const math::Matrix4f& projection )
            {
                self.spatial->setProjection( projection );
            }
        )
        .def_property( "orthogonal_projection_hint",
            []( SpatialView< Camera >& self )->bool
            {
                return self.spatial->isOrthogonalProjectionHintSet();
            },
            []( SpatialView< Camera >& self, bool orthogonalProjectionHint )
            {
                self.spatial->setOrthogonalProjectionHint( orthogonalProjectionHint );
            }
        )
        .def_property_readonly( "view_transform",
            []( SpatialView< Camera >& self )->const math::Matrix4f&
            {
                return self.spatial->viewTransform();
            }
        );

        auto _Geometry = py::class_< SpatialView< Geometry >, std::shared_ptr< SpatialView< Geometry > > >( m, "Geometry" );
        addInterface_Spatial< Geometry >( _Geometry )
            .def( py::init< unsigned int, const std::string& >(), "geometry_type"_a, "tag"_a = "" )
            /*
            .def( "put_feature", &Geometry::putFeature )
            .def( "remove_feature", py::overload_cast< GeometryFeature& >( &Geometry::removeFeature ) )
            .def( "remove_feature_role", py::overload_cast< unsigned int >( &Geometry::removeFeature ) )
            .def( "clear_features", &Geometry::clearFeatures )
            .def( "has_feature", py::overload_cast< const GeometryFeature& >( &Geometry::hasFeature, py::const_ ) )
            .def( "has_feature_role", py::overload_cast< unsigned int >( &Geometry::hasFeature, py::const_ ) )
            .def( "feature", &Geometry::feature, py::return_value_policy::reference )
            .def( "features_count", &Geometry::featuresCount )
            .def_property( "bounding_volume", py::overload_cast<>( &Geometry::boundingVolume, py::const_ ), &Geometry::setBoundingVolume )
            .def_property_readonly( "has_bounding_volume", &Geometry::hasBoundingVolume )
            .def_readonly( "geometry_type", &Geometry::geometryType )
            */;

/*
    py::class_< GeometryFeature, std::unique_ptr< GeometryFeature, py::nodelete > >( m, "GeometryFeature" )
        .def( "release", &GeometryFeature::release );

    py::class_< Material, GeometryFeature, std::unique_ptr< Material, py::nodelete > >( m, "Material" )
        .def_static( "create", []( const std::string& shaderName )
        {
            return &Material::create( shaderName );
        }
        , py::return_value_policy::reference, "shaderName"_a )
        .def( "set_parameter4f", &Material::setParameter< math::Vector4f > )
        .def( "set_parameter3f", &Material::setParameter< math::Vector4f > )
        .def( "set_parameter2f", &Material::setParameter< math::Vector4f > )
        .def( "clear_parameters", &Material::clearParameters )
        .def( "remove_parameter", &Material::removeParameter )
        .def( "has_parameter", &Material::hasParameter );

    py::class_< BoundingVolume, std::unique_ptr< BoundingVolume, py::nodelete > >( m, "BoundingVolume" );

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
