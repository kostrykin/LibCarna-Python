#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/py/helpers.h>
#include <Carna/base/BufferedIntensityVolume.h>
#include <Carna/helpers/FrameRendererHelper.h>
#include <Carna/helpers/VolumeGridHelper.h>
#include <Carna/helpers/VolumeGridHelperDetails.h>
/*
#include <Carna/base/glew.h>
#include <Carna/base/Color.h>
#include <Carna/base/Geometry.h>
#include <Carna/helpers/FrameRendererHelper.h>
#include <Carna/helpers/PointMarkerHelper.h>
*/

using namespace Carna::py;
using namespace Carna::py::base;
using namespace Carna::py::helpers;



// ----------------------------------------------------------------------------------
// addVolumeGridHelperIntensityComponent
// ----------------------------------------------------------------------------------

template< typename VolumeGridHelperType, typename VolumeGridHelperClass >
void addVolumeGridHelperIntensityComponent( VolumeGridHelperClass& cls )
{
    const static auto DEFAULT_ROLE_INTENSITIES = VolumeGridHelperType::DEFAULT_ROLE_INTENSITIES;
    cls.def_readonly_static(
        "DEFAULT_ROLE_INTENSITIES",
        &DEFAULT_ROLE_INTENSITIES
    );
    cls.def_property(
        "intensities_role",
        &VolumeGridHelperType::intensitiesRole,
        &VolumeGridHelperType::setIntensitiesRole 
    );
}



// ----------------------------------------------------------------------------------
// addVolumeGridHelperNormalsComponent
// ----------------------------------------------------------------------------------

template< typename VolumeGridHelperType, typename VolumeGridHelperClass >
void addVolumeGridHelperNormalsComponent( VolumeGridHelperClass& cls )
{
    const static auto DEFAULT_ROLE_NORMALS = VolumeGridHelperType::DEFAULT_ROLE_NORMALS;
    cls.def_readonly_static(
        "DEFAULT_ROLE_NORMALS",
        &DEFAULT_ROLE_NORMALS
    );
    cls.def_property(
        "normals_role",
        &VolumeGridHelperType::normalsRole,
        &VolumeGridHelperType::setNormalsRole 
    );
}



// ----------------------------------------------------------------------------------
// defineVolumeGridHelper
// ----------------------------------------------------------------------------------

const static auto VolumeGridHelperBase__DEFAULT_MAX_SEGMENT_BYTESIZE = \
    ([](){ return Carna::helpers::VolumeGridHelperBase::DEFAULT_MAX_SEGMENT_BYTESIZE; })();


template< typename VolumeGridHelperType, typename VolumeGridHelperClass >
void defineVolumeGridHelper( VolumeGridHelperClass& cls )
{
    cls
        .def(
            py::init< const Carna::base::math::Vector3ui&, std::size_t >(),
            "native_resolution"_a, "max_segment_bytesize"_a = VolumeGridHelperBase__DEFAULT_MAX_SEGMENT_BYTESIZE
        )
        .def(
            "load_intensities",
            []( VolumeGridHelperType& self, py::array_t< double > intensityData )
            {
                const auto rawData = intensityData.unchecked< 3 >();
                return self.loadIntensities(
                    [ &rawData ]( const Carna::base::math::Vector3ui& voxel )
                    {
                        return static_cast< float >( rawData( voxel.x(), voxel.y(), voxel.z() ) );
                    }
                );
            }
            , "intensity_data"_a )
        /*
        .def( "create_node", py::overload_cast< unsigned int, const VolumeGridHelperBase::Spacing& >( &VolumeGridHelperType::createNode, py::const_ ), py::return_value_policy::reference )
        .def( "create_node", py::overload_cast< unsigned int, const VolumeGridHelperBase::Dimensions& >( &VolumeGridHelperType::createNode, py::const_ ), py::return_value_policy::reference )
        .def( "release_geometry_features", &VolumeGridHelperType::releaseGeometryFeatures )
        .DEF_FREE( VolumeGridHelperType );
        */
        .doc() = R"(Computes the partitioning grid of volume data and the corresponding normal map. Also creates scene
        nodes that represent the volume data within a scene.
        
        Arguments:
            native_resolution: The resolution the partitioning grid is to be prepared for. This is the resolution that
                will be expected when the data is loaded.
            max_segment_bytesize: Maximum memory size of a single volume segment in bytes. Determines the partitioning
                of the volume into a regular grid of segments.)";
}



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

#ifdef BUILD_HELPERS_MODULE
PYBIND11_MODULE( helpers, m )
{

    py::class_< FrameRendererHelperView >( m, "FrameRendererHelper" )
        .def( py::init< const std::shared_ptr< FrameRendererView >& >() )
        .def( "add_stage", &FrameRendererHelperView::add_stage, "stage"_a )
        .def( "commit", &FrameRendererHelperView::commit )
        .def( "reset", &FrameRendererHelperView::reset );

    py::class_< Carna::helpers::VolumeGridHelperBase >( m, "VolumeGridHelperBase" )
        .def_readonly_static( "DEFAULT_MAX_SEGMENT_BYTESIZE", &VolumeGridHelperBase__DEFAULT_MAX_SEGMENT_BYTESIZE )
        .def_readonly( "native_resolution", &Carna::helpers::VolumeGridHelperBase::nativeResolution );

    py::class_< Carna::helpers::VolumeGridHelperBase::Spacing >( m, "Spacing" )
        .def( py::init< const Carna::base::math::Vector3f& >() )
        .def_readwrite( "millimeters", &Carna::helpers::VolumeGridHelperBase::Spacing::millimeters )
        .doc() = "Specifies the spacing between two adjacent voxel centers.";

    py::class_< Carna::helpers::VolumeGridHelperBase::Dimensions >( m, "Dimensions" )
        .def( py::init< const Carna::base::math::Vector3f& >() )
        .def_readwrite( "millimeters", &Carna::helpers::VolumeGridHelperBase::Dimensions::millimeters )
        .doc() = "Specifies the spatial size of the whole dataset.";

    auto VolumeGridHelper_IntensityVolumeUInt16 = py::class_<
        Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16 >,
        Carna::helpers::VolumeGridHelperBase
    >( m, "VolumeGridHelper_IntensityVolumeUInt16" );
    defineVolumeGridHelper<
        Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16 >
    >(
        VolumeGridHelper_IntensityVolumeUInt16
    );
    addVolumeGridHelperIntensityComponent< Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16 > >(
        VolumeGridHelper_IntensityVolumeUInt16
    );

    auto VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8 = py::class_<
        Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16, Carna::base::NormalMap3DInt8 >,
        Carna::helpers::VolumeGridHelperBase
    >( m, "VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8" );
    defineVolumeGridHelper<
        Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16, Carna::base::NormalMap3DInt8 >
    >(
        VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8
    );
    addVolumeGridHelperIntensityComponent<
        Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16, Carna::base::NormalMap3DInt8 >
    >(
        VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8
    );
    addVolumeGridHelperNormalsComponent<
        Carna::helpers::VolumeGridHelper< Carna::base::IntensityVolumeUInt16, Carna::base::NormalMap3DInt8 >
    >(
        VolumeGridHelper_IntensityVolumeUInt16_NormalMap3DInt8
    );

    /*
    defineVolumeGridHelper< VolumeGridHelper< IntensityVolumeUInt8 > >( m, "VolumeGrid_UInt8Intensity" );
    defineVolumeGridHelper< VolumeGridHelper< IntensityVolumeUInt8, NormalMap3DInt8 > >( m, "VolumeGrid_UInt8Intensity_Int8Normal" );
    */

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
    */

}
#endif // BUILD_HELPERS_MODULE