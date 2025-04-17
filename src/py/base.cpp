#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

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



PYBIND11_MODULE( base, m )
{

    py::class_< Carna::base::GLContext >( m, "GLContext" );

    py::class_< Spatial >( m, "Spatial" )
        .def_property_readonly( "has_parent", &Spatial::hasParent )
        .def( "detach_from_parent", &Spatial::detachFromParent )
        .def_property_readonly( "parent", py::overload_cast<>( &Spatial::parent, py::const_ ) )
        .def( "find_root", py::overload_cast<>( &Spatial::findRoot, py::const_ ) )
        .def_property( "movable", &Spatial::isMovable, &Spatial::setMovable )
        .def_property( "tag", &Spatial::tag, &Spatial::setTag )
        .def_readwrite( "local_transform", &Spatial::localTransform );

    py::class_< Node, Spatial >( m, "Node" )
        .def( py::init< const std::string& >(), "tag"_a = "" )
        .def( "attach_child", &Node::attachChild, py::keep_alive<2, 1>() )
        .def( "detach_child", &Node::detachChild )
        .def( "has_child", &Node::hasChild )
        .def( "delete_all_children", &Node::deleteAllChildren )
        .def( "children", &Node::children );

/*
    py::class_< Camera, Spatial >( m, "Camera" )
        .def_static( "create", []()
        {
            return new Camera();
        }
        , py::return_value_policy::reference )
        .def_property( "projection", &Camera::projection, &Camera::setProjection )
        .def_property( "orthogonal_projection_hint", &Camera::isOrthogonalProjectionHintSet, &Camera::setOrthogonalProjectionHint )
        .def_property_readonly( "view_transform", &Camera::viewTransform );

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

    py::class_< Geometry, Spatial >( m, "Geometry" )
        .def_static( "create", []( const unsigned int geometryType, const std::string& tag )
        {
            return new Geometry( geometryType, tag );
        }
        , py::return_value_policy::reference, "geometryType"_a, "tag"_a = "" )
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
        .def_readonly( "geometry_type", &Geometry::geometryType );

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
