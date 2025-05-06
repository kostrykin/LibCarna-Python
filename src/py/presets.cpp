#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <LibCarna/base/GLContext.hpp>
#include <LibCarna/base/Color.hpp>
#include <LibCarna/presets/MaskRenderingStage.hpp>
#include <LibCarna/presets/MIPStage.hpp>
#include <LibCarna/presets/CuttingPlanesStage.hpp>
#include <LibCarna/presets/DVRStage.hpp>
#include <LibCarna/presets/DRRStage.hpp>
#include <LibCarna/py/presets.hpp>
/*
#include <LibCarna/base/GLContext.hpp>
#include <LibCarna/base/ManagedMesh.hpp>
#include <LibCarna/presets/OccludedRenderingStage.hpp>
#include <LibCarna/presets/OpaqueRenderingStage.hpp>
*/

using namespace LibCarna::py;
using namespace LibCarna::py::base;
using namespace LibCarna::py::presets;

/*
void CuttingPlanesStage__set_windowing( CuttingPlanesStage* self, float min, float max )
{
    const auto level = (min + max) / 2;
    const auto width =  max - min;
    self->setWindowingLevel( level );
    self->setWindowingWidth( width );
}
*/



// ----------------------------------------------------------------------------------
// OpaqueRenderingStageView
// ----------------------------------------------------------------------------------

OpaqueRenderingStageView::OpaqueRenderingStageView( unsigned int geometryType )
    : MeshRenderingStageView::MeshRenderingStageView( new LibCarna::presets::OpaqueRenderingStage( geometryType ) )
{
}


LibCarna::presets::OpaqueRenderingStage& OpaqueRenderingStageView::opaqueRenderingStage()
{
    return static_cast< LibCarna::presets::OpaqueRenderingStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// VolumeRenderingStageView
// ----------------------------------------------------------------------------------

const unsigned int VolumeRenderingStageView::DEFAULT_SAMPLE_RATE = LibCarna::presets::VolumeRenderingStage::DEFAULT_SAMPLE_RATE;


VolumeRenderingStageView::VolumeRenderingStageView( LibCarna::presets::VolumeRenderingStage* renderStage )
    : RenderStageView::RenderStageView( renderStage )
{
}


LibCarna::presets::VolumeRenderingStage& VolumeRenderingStageView::volumeRenderingStage()
{
    return static_cast< LibCarna::presets::VolumeRenderingStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// MaskRenderingStageView
// ----------------------------------------------------------------------------------

MaskRenderingStageView::MaskRenderingStageView( unsigned int geometryType, unsigned int maskRole )
    : VolumeRenderingStageView::VolumeRenderingStageView(
        new LibCarna::presets::MaskRenderingStage( geometryType, maskRole )
    )
{
}


LibCarna::presets::MaskRenderingStage& MaskRenderingStageView::maskRenderingStage()
{
    return static_cast< LibCarna::presets::MaskRenderingStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// MIPStageView
// ----------------------------------------------------------------------------------

const static auto MIP_STAGE__ROLE_INTENSITIES = LibCarna::presets::MIPStage::ROLE_INTENSITIES;


MIPStageView::MIPStageView( unsigned int geometryType )
    : VolumeRenderingStageView::VolumeRenderingStageView(
        new LibCarna::presets::MIPStage( geometryType )
    )
{
}


LibCarna::presets::MIPStage& MIPStageView::mipStage()
{
    return static_cast< LibCarna::presets::MIPStage& >( *renderStage );
}

std::shared_ptr< base::ColorMapView > MIPStageView::colorMap()
{
    return std::shared_ptr< base::ColorMapView >(
        new base::ColorMapView( this->shared_from_this(), mipStage().colorMap )
    );
}



// ----------------------------------------------------------------------------------
// CuttingPlanesStageView
// ----------------------------------------------------------------------------------

const static auto CUTTING_PLANES_STAGE__ROLE_INTENSITIES = LibCarna::presets::CuttingPlanesStage::ROLE_INTENSITIES;


CuttingPlanesStageView::CuttingPlanesStageView( unsigned int volumeGeometryType, unsigned int planeGeometryType )
    : RenderStageView::RenderStageView(
        new LibCarna::presets::CuttingPlanesStage( volumeGeometryType, planeGeometryType )
    )
{
}


LibCarna::presets::CuttingPlanesStage& CuttingPlanesStageView::cuttingPlanesStage()
{
    return static_cast< LibCarna::presets::CuttingPlanesStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// DVRStageView
// ----------------------------------------------------------------------------------

const static auto DVR_STAGE__ROLE_INTENSITIES = LibCarna::presets::DVRStage::ROLE_INTENSITIES;
const static auto DVR_STAGE__ROLE_NORMALS     = LibCarna::presets::DVRStage::ROLE_NORMALS;


DVRStageView::DVRStageView( unsigned int geometryType )
    : VolumeRenderingStageView::VolumeRenderingStageView(
        new LibCarna::presets::DVRStage( geometryType )
    )
{
}


LibCarna::presets::DVRStage& DVRStageView::dvrStage()
{
    return static_cast< LibCarna::presets::DVRStage& >( *renderStage );
}

std::shared_ptr< base::ColorMapView > DVRStageView::colorMap()
{
    return std::shared_ptr< base::ColorMapView >(
        new base::ColorMapView( this->shared_from_this(), dvrStage().colorMap )
    );
}



// ----------------------------------------------------------------------------------
// DRRStageView
// ----------------------------------------------------------------------------------

const static auto DRR_STAGE__ROLE_INTENSITIES = LibCarna::presets::DRRStage::ROLE_INTENSITIES;


DRRStageView::DRRStageView( unsigned int geometryType )
    : VolumeRenderingStageView::VolumeRenderingStageView(
        new LibCarna::presets::DRRStage( geometryType )
    )
{
}


LibCarna::presets::DRRStage& DRRStageView::drrStage()
{
    return static_cast< LibCarna::presets::DRRStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// PYBIND11_MODULE: presets
// ----------------------------------------------------------------------------------

PYBIND11_MODULE( presets, m )
{

    /* OpaqueRenderingStage
     */
    py::class_< OpaqueRenderingStageView, std::shared_ptr< OpaqueRenderingStageView >, MeshRenderingStageView >(
        m, "OpaqueRenderingStage"
    )
        .def( py::init< unsigned int >(), "geometry_type"_a )
        .def_property_readonly( "geometry_type",
            VIEW_DELEGATE( OpaqueRenderingStageView, opaqueRenderingStage().LibCarna::base::MeshRenderingMixin::geometryType )
        )
        .doc() = R"(Renders *opaque meshes* in the scene.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. OpaqueRenderingStage: example-setup-start
           :end-before: # .. OpaqueRenderingStage: example-setup-end
           :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.OpaqueRenderingStage.test__animated.png
           :width: 400)";

    /* VolumeRenderingStage
     */
    py::class_< VolumeRenderingStageView, std::shared_ptr< VolumeRenderingStageView >, RenderStageView >(
        m, "VolumeRenderingStage"
    )
        .def_readonly_static( "DEFAULT_SAMPLE_RATE", &VolumeRenderingStageView::DEFAULT_SAMPLE_RATE )
        .def_property_readonly( "geometry_type",
            VIEW_DELEGATE( VolumeRenderingStageView, volumeRenderingStage().geometryType )
        )
        .def_property( "sample_rate",
            VIEW_DELEGATE( VolumeRenderingStageView, volumeRenderingStage().sampleRate() ),
            VIEW_DELEGATE( VolumeRenderingStageView, volumeRenderingStage().setSampleRate( sampleRate ), unsigned int sampleRate )
        );
    
    /* MaskRenderingStage
     *
     * `color` is not bound as a property, to prevent assignments of the form `.color.r = 0`, which would not work.
     */
    py::class_< MaskRenderingStageView, std::shared_ptr< MaskRenderingStageView >, VolumeRenderingStageView >(
        m, "MaskRenderingStage"
    )
        .def_readonly_static( "DEFAULT_ROLE_MASK", &LibCarna::presets::MaskRenderingStage::DEFAULT_ROLE_MASK )
        .def_readonly_static( "DEFAULT_COLOR", &LibCarna::presets::MaskRenderingStage::DEFAULT_COLOR )
        .def(
            py::init< unsigned int, unsigned int >(),
            "geometry_type"_a, "mask_role"_a = LibCarna::presets::MaskRenderingStage::DEFAULT_ROLE_MASK
        )
        .def_property_readonly(
            "mask_role",
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().maskRole )
        )
        .def(
            "color",
            VIEW_DELEGATE( MaskRenderingStageView,  maskRenderingStage().color() )
        )
        .def(
            "set_color",
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().setColor( color ), const LibCarna::base::Color& color )
        )
        .def_property(
            "render_borders",
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().renderBorders() ),
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().setRenderBorders( renderBorders ), bool renderBorders )
        )
        .doc() = R"(Renders 3D masks as either unshaded areas or borders.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. MaskRenderingStage: example-setup-start
           :end-before: # .. MaskRenderingStage: example-setup-end
           :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.MaskRenderingStage.test__animated.png
           :width: 400)";
    
    /* MIPStage
     */
    py::class_< MIPStageView, std::shared_ptr< MIPStageView >, VolumeRenderingStageView >( m, "MIPStage" )
        .def_readonly_static( "ROLE_INTENSITIES", &MIP_STAGE__ROLE_INTENSITIES )
        .def( py::init< unsigned int >(), "geometry_type"_a )
        .def_property_readonly( "color_map", &MIPStageView::colorMap )
        .doc() = R"(Renders *maximum intensity projections* of volume geometries in the scene.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. MIPStage: example-setup-start
           :end-before: # .. MIPStage: example-setup-end
           :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.MIPStage.test__animated.png
           :width: 400)";
    
    /* CuttingPlanesStage
     */
    py::class_< CuttingPlanesStageView, std::shared_ptr< CuttingPlanesStageView >, RenderStageView >( m, "CuttingPlanesStage" )
        .def_readonly_static( "ROLE_INTENSITIES", &CUTTING_PLANES_STAGE__ROLE_INTENSITIES )
        .def_readonly_static( "DEFAULT_WINDOWING_WIDTH", &LibCarna::presets::CuttingPlanesStage::DEFAULT_WINDOWING_WIDTH )
        .def_readonly_static( "DEFAULT_WINDOWING_LEVEL", &LibCarna::presets::CuttingPlanesStage::DEFAULT_WINDOWING_LEVEL )
        .def( py::init< unsigned int, unsigned int >(), "volume_geometry_type"_a, "plane_geometry_type"_a )
        .def_property_readonly( "volume_geometry_type",
            VIEW_DELEGATE( CuttingPlanesStageView, cuttingPlanesStage().volumeGeometryType )
        )
        .def_property_readonly( "plane_geometry_type",
            VIEW_DELEGATE( CuttingPlanesStageView, cuttingPlanesStage().planeGeometryType )
        )
        .def_property(
            "windowing_width",
            VIEW_DELEGATE( CuttingPlanesStageView, cuttingPlanesStage().windowingWidth() ),
            VIEW_DELEGATE( CuttingPlanesStageView, cuttingPlanesStage().setWindowingWidth( windowingWidth ), float windowingWidth )
        )
        .def_property(
            "windowing_level",
            VIEW_DELEGATE( CuttingPlanesStageView, cuttingPlanesStage().windowingLevel() ),
            VIEW_DELEGATE( CuttingPlanesStageView, cuttingPlanesStage().setWindowingLevel( windowingLevel ), float windowingLevel )
        )
        .doc() = R"(Renders *cutting planes* of volume geometries in the scene.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. CuttingPlanesStage: example-setup-start
           :end-before: # .. CuttingPlanesStage: example-setup-end
           :dedent: 8

        The normal vector of the planes does not have to necessarily align with the axes.

        In this example, we have a z-plane and a pair of x-planes. The x-planes are positioned on the left and right
        faces of the volume. Their distances to the center of the volume calculates as the width of the volume divided
        by 2, and the width of the volume is 63 units (64 voxels, with voxels on the x-axis spaced by 1 unit).

        For a more information-rich visualization of the volume, we will make the z-plane bounce between the front and
        back faces of the volume. The amplitude is calculated as the depth of the volume divided by 2, and the depth of
        the volume is 38 units (19 voxels, and voxels on the z-axis are spaced by 2 unit).

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. CuttingPlanesStage: example-animation-start
           :end-before: # .. CuttingPlanesStage: example-animation-end
           :dedent: 8

        The example yields this animation:

        .. image:: ../test/results/expected/test_integration.CuttingPlanesStage.test__animated.png
           :width: 400)";
    
    /* DVRStage
     */
    py::class_< DVRStageView, std::shared_ptr< DVRStageView >, VolumeRenderingStageView >( m, "DVRStage" )
        .def_readonly_static( "ROLE_INTENSITIES", &DVR_STAGE__ROLE_INTENSITIES )
        .def_readonly_static( "ROLE_NORMALS", &DVR_STAGE__ROLE_NORMALS )
        .def_readonly_static( "DEFAULT_TRANSLUCENCY", &LibCarna::presets::DVRStage::DEFAULT_TRANSLUCENCY )
        .def_readonly_static( "DEFAULT_DIFFUSE_LIGHT", &LibCarna::presets::DVRStage::DEFAULT_DIFFUSE_LIGHT )
        .def( py::init< unsigned int >(), "geometry_type"_a )
        .def_property_readonly( "color_map", &DVRStageView::colorMap )
        .def_property(
            "translucency",
            VIEW_DELEGATE( DVRStageView, dvrStage().translucency() ),
            VIEW_DELEGATE( DVRStageView, dvrStage().setTranslucency( translucency ), float translucency )
        )
        .def_property(
            "diffuse_light",
            VIEW_DELEGATE( DVRStageView, dvrStage().diffuseLight() ),
            VIEW_DELEGATE( DVRStageView, dvrStage().setDiffuseLight( diffuseLight ), float diffuseLight )
        )
        .doc() = R"(Performs *direct volume rendering* of the volume geometries in the scene.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. DVRStage: example-setup-start
           :end-before: # .. DVRStage: example-setup-end
           :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.DVRStage.test__animated.png
           :width: 400)";
    
    /* DRRStage
     */
    py::class_< DRRStageView, std::shared_ptr< DRRStageView >, VolumeRenderingStageView >( m, "DRRStage" )
        .def_readonly_static( "ROLE_INTENSITIES", &DVR_STAGE__ROLE_INTENSITIES )
        .def_readonly_static( "DEFAULT_WATER_ATTENUATION", &LibCarna::presets::DRRStage::DEFAULT_WATER_ATTENUATION )
        .def_readonly_static( "DEFAULT_BASE_INTENSITY", &LibCarna::presets::DRRStage::DEFAULT_BASE_INTENSITY )
        .def_readonly_static( "DEFAULT_LOWER_THRESHOLD", &LibCarna::presets::DRRStage::DEFAULT_LOWER_THRESHOLD.value )
        .def_readonly_static( "DEFAULT_UPPER_THRESHOLD", &LibCarna::presets::DRRStage::DEFAULT_UPPER_THRESHOLD.value )
        .def_readonly_static( "DEFAULT_UPPER_MULTIPLIER", &LibCarna::presets::DRRStage::DEFAULT_UPPER_MULTIPLIER )
        .def_readonly_static( "DEFAULT_RENDER_INVERSE", &LibCarna::presets::DRRStage::DEFAULT_RENDER_INVERSE )
        .def( py::init< unsigned int >(), "geometry_type"_a )
        .def_property(
            "water_attenuation",
            VIEW_DELEGATE( DRRStageView, drrStage().waterAttenuation() ),
            VIEW_DELEGATE( DRRStageView, drrStage().setWaterAttenuation( waterAttenuation ), float waterAttenuation )
        )
        .def_property(
            "base_intensity",
            VIEW_DELEGATE( DRRStageView, drrStage().baseIntensity() ),
            VIEW_DELEGATE( DRRStageView, drrStage().setBaseIntensity( baseIntensity ), float baseIntensity )
        )
        .def_property(
            "lower_threshold",
            VIEW_DELEGATE( DRRStageView, drrStage().lowerThreshold().value ),
            VIEW_DELEGATE( DRRStageView, drrStage().setLowerThreshold( LibCarna::base::HUV( lowerThreshold ) ), short lowerThreshold )
        )
        .def_property(
            "upper_threshold",
            VIEW_DELEGATE( DRRStageView, drrStage().upperThreshold().value ),
            VIEW_DELEGATE( DRRStageView, drrStage().setUpperThreshold( LibCarna::base::HUV(upperThreshold ) ), short upperThreshold )
        )
        .def_property(
            "upper_multiplier",
            VIEW_DELEGATE( DRRStageView, drrStage().upperMultiplier() ),
            VIEW_DELEGATE( DRRStageView, drrStage().setUpperMultiplier( upperMultiplier ), float upperMultiplier )
        )
        .def_property(
            "render_inverse",
            VIEW_DELEGATE( DRRStageView, drrStage().isRenderingInverse() ),
            VIEW_DELEGATE( DRRStageView, drrStage().setRenderingInverse( renderInverse ), bool renderInverse )
        )
        .doc() = R"(Performs *digital radiograph reconstruction* of the volume geometries in the scene.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. DRRStage: example-setup-start
           :end-before: # .. DRRStage: example-setup-end
           :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.DRRStage.test__animated.png
           :width: 400)";

/*
    py::class_< OccludedRenderingStage, RenderStage >( m, "OccludedRenderingStage" )
        .def_static( "create", []()
        {
            return new OccludedRenderingStage();
        }
        , py::return_value_policy::reference )
        .def_property_readonly_static( "DEFAULT_OCCLUSION_TRANSLUCENCY", []( py::object ) { return OccludedRenderingStage::DEFAULT_OCCLUSION_TRANSLUCENCY; } )
        .def_property( "occlusion_translucency", &OccludedRenderingStage::occlusionTranslucency, &OccludedRenderingStage::setOcclusionTranslucency )
        .def( "disable_all_stages", &OccludedRenderingStage::disableAllStages )
        .def( "enable_stage", &OccludedRenderingStage::enableStage )
        .def( "disable_stage", &OccludedRenderingStage::disableStage )
        .def( "is_stage_enabled", &OccludedRenderingStage::isStageEnabled );
*/

}