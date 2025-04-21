#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/py/helpers.h>
#include <Carna/helpers/FrameRendererHelper.h>
/*
#include <Carna/base/glew.h>
#include <Carna/base/Color.h>
#include <Carna/base/Geometry.h>
#include <Carna/base/BufferedIntensityVolume.h>
#include <Carna/helpers/FrameRendererHelper.h>
#include <Carna/helpers/PointMarkerHelper.h>
#include <Carna/helpers/VolumeGridHelper.h>
*/

using namespace Carna::py;
using namespace Carna::py::base;
using namespace Carna::py::helpers;



// ----------------------------------------------------------------------------------
// defineVolumeGridHelper
// ----------------------------------------------------------------------------------

/*
template< typename VolumeGridHelperType, typename Module >
void defineVolumeGridHelper( Module& m, const char* name )
{
    auto cl = py::class_< VolumeGridHelperType, VolumeGridHelperBase >( m, name )
        .def_static( "create", []( const math::Vector3ui& nativeResolution, std::size_t maxSegmentBytesize )
        {
            return new VolumeGridHelperType( nativeResolution, maxSegmentBytesize );
        }
        , py::return_value_policy::reference, "nativeResolution"_a, "maxSegmentBytesize"_a = ([](){ return VolumeGridHelperBase::DEFAULT_MAX_SEGMENT_BYTESIZE; })() )
        .def( "load_data", []( VolumeGridHelperType* self, py::array_t< double > data, bool test )
        {
            const auto rawData = data.unchecked< 3 >();
            const auto voxel2intensity = [ &rawData, test ]( const math::Vector3ui voxel )
            {
                if (test) {
                    return 0.f;
                }
                else return static_cast< float >( rawData( voxel.x(), voxel.y(), voxel.z() ) );
            };
            return self->loadIntensities( voxel2intensity );
        }
        , "data"_a, "test"_a = false )
        .def_property( "intensities_role", &VolumeGridHelperType::intensitiesRole, &VolumeGridHelperType::setIntensitiesRole )
        .def( "create_node", py::overload_cast< unsigned int, const VolumeGridHelperBase::Spacing& >( &VolumeGridHelperType::createNode, py::const_ ), py::return_value_policy::reference )
        .def( "create_node", py::overload_cast< unsigned int, const VolumeGridHelperBase::Dimensions& >( &VolumeGridHelperType::createNode, py::const_ ), py::return_value_policy::reference )
        .def( "release_geometry_features", &VolumeGridHelperType::releaseGeometryFeatures )
        .DEF_FREE( VolumeGridHelperType );
}
*/



// ----------------------------------------------------------------------------------
// FrameRendererHelperView
// ----------------------------------------------------------------------------------

FrameRendererHelperView::FrameRendererHelperView( const std::shared_ptr< Carna::py::base::FrameRendererView >& frameRendererView )
    : frameRendererView( frameRendererView )
{
}


void FrameRendererHelperView::add_stage( const std::shared_ptr< Carna::py::base::RenderStageView >& stage )
{
    stages.push_back( stage );
}


void FrameRendererHelperView::reset()
{
    stages.clear();
}


void FrameRendererHelperView::commit()
{
    /* Verify that the render stages are not already added to another frame renderer.
     */
    for( const std::shared_ptr< Carna::py::base::RenderStageView >& rsView : stages )
    {
        CARNA_ASSERT_EX( rsView->ownedBy.get() == nullptr, "Render stage was already added to a frame renderer." );
    }
    
    /* Add the render stages to the frame renderer (that also takes the ownership).
     * 
     * Note that there might be still `RenderStageView` objects around, that reference
     * the render stages that are currently inside the targeted frame renderer. Hence,
     * we are not allowed to clear the frame renderer here.
     */
    Carna::helpers::FrameRendererHelper< > frameRendererHelper( frameRendererView->frameRenderer );
    for( const std::shared_ptr< Carna::py::base::RenderStageView >& rsView : stages )
    {
        rsView->ownedBy = frameRendererView;
        frameRendererHelper << rsView->renderStage;
    }

    frameRendererHelper.commit( false );
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: helpers
// ----------------------------------------------------------------------------------

/*
const static auto VolumeGridHelperBase__DEFAULT_MAX_SEGMENT_BYTESIZE = ([](){ return VolumeGridHelperBase::DEFAULT_MAX_SEGMENT_BYTESIZE; })();
*/


#ifdef BUILD_HELPERS_MODULE
PYBIND11_MODULE( helpers, m )
{

    py::class_< FrameRendererHelperView >( m, "FrameRendererHelper" )
        .def( py::init< const std::shared_ptr< FrameRendererView >& >() )
        .def( "add_stage", &FrameRendererHelperView::add_stage, "stage"_a )
        .def( "commit", &FrameRendererHelperView::commit )
        .def( "reset", &FrameRendererHelperView::reset );

    /*
    const static auto PointMarkerHelper__DEFAULT_POINT_SIZE = ([](){ return PointMarkerHelper::DEFAULT_POINT_SIZE; })();

    py::class_< PointMarkerHelper >( m, "PointMarkerHelper" )
        .def_static( "create", []( unsigned int geometryType, unsigned int pointSize )
        {
            return new PointMarkerHelper( geometryType, pointSize );
        }
        , py::return_value_policy::reference, "geometryType"_a, "pointSize"_a = PointMarkerHelper__DEFAULT_POINT_SIZE )
        .def_static( "create_ext", []( unsigned int geometryType, unsigned int meshRole, unsigned int materialRole, unsigned int pointSize )
        {
            return new PointMarkerHelper( geometryType, meshRole, materialRole, pointSize );
        }
        , py::return_value_policy::reference, "geometryType"_a, "meshRole"_a, "materialRole"_a, "pointSize"_a = PointMarkerHelper__DEFAULT_POINT_SIZE )
        .def_readonly_static( "DEFAULT_POINT_SIZE", &PointMarkerHelper__DEFAULT_POINT_SIZE )
        .def( "release_geometry_features", &PointMarkerHelper::releaseGeometryFeatures )
        .def( "create_point_marker", []( const PointMarkerHelper* helper, unsigned int* pointSize, const math::Vector4f* color )
        {
            if( pointSize == nullptr && color == nullptr ) return helper->createPointMarker();
            if( pointSize == nullptr && color != nullptr ) return helper->createPointMarker( *color );
            if( pointSize != nullptr && color == nullptr ) return helper->createPointMarker( *pointSize );
            if( pointSize != nullptr && color != nullptr ) return helper->createPointMarker( *color, *pointSize );
        }
        , py::return_value_policy::reference, "pointSize"_a = nullptr, "color"_a = nullptr )
        .def_readonly( "geometry_type", &PointMarkerHelper::geometryType )
        .def_readonly( "mesh_role", &PointMarkerHelper::meshRole )
        .def_readonly( "material_role", &PointMarkerHelper::materialRole )
        .def_readonly( "point_size", &PointMarkerHelper::pointSize )
        .def_static( "reset_default_color", &PointMarkerHelper::resetDefaultColor )
        .DEF_FREE( PointMarkerHelper );

    py::class_< VolumeGridHelperBase >( m, "VolumeGridHelperBase" )
        .def_readonly_static( "DEFAULT_MAX_SEGMENT_BYTESIZE", &VolumeGridHelperBase__DEFAULT_MAX_SEGMENT_BYTESIZE );

    py::class_< VolumeGridHelperBase::Spacing >( m, "Spacing" )
        .def( py::init< const math::Vector3f& >() );

    py::class_< VolumeGridHelperBase::Dimensions >( m, "Dimensions" )
        .def( py::init< const math::Vector3f& >() );

    defineVolumeGridHelper< VolumeGridHelper< IntensityVolumeUInt16 > >( m, "VolumeGrid_UInt16Intensity" );
    defineVolumeGridHelper< VolumeGridHelper< IntensityVolumeUInt16, NormalMap3DInt8 > >( m, "VolumeGrid_UInt16Intensity_Int8Normal" );

    defineVolumeGridHelper< VolumeGridHelper< IntensityVolumeUInt8 > >( m, "VolumeGrid_UInt8Intensity" );
    defineVolumeGridHelper< VolumeGridHelper< IntensityVolumeUInt8, NormalMap3DInt8 > >( m, "VolumeGrid_UInt8Intensity_Int8Normal" );

    py::class_< FrameRendererHelper< > >( m, "FrameRendererHelper" )
        .def( py::init< RenderStageSequence& >() )
        .def( "add_stage", &FrameRendererHelper< >::operator<< )
        .def( "reset", &FrameRendererHelper< >::reset )
        .def( "commit", &FrameRendererHelper< >::commit, "clear"_a = true );
    */

}
#endif // BUILD_HELPERS_MODULE