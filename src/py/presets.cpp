#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/GLContext.h>
#include <Carna/base/Color.h>
#include <Carna/presets/MaskRenderingStage.h>
#include <Carna/presets/MIPLayer.h>
#include <Carna/presets/MIPStage.h>
#include <Carna/presets/CuttingPlanesStage.h>
#include <Carna/py/presets.h>
/*
#include <Carna/base/GLContext.h>
#include <Carna/base/ManagedMesh.h>
#include <Carna/presets/DRRStage.h>
#include <Carna/presets/DVRStage.h>
#include <Carna/presets/MIPLayer.h>
#include <Carna/presets/MIPStage.h>
#include <Carna/presets/OccludedRenderingStage.h>
#include <Carna/presets/OpaqueRenderingStage.h>
*/

using namespace Carna::py;
using namespace Carna::py::base;
using namespace Carna::py::presets;

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
    : MeshRenderingStageView::MeshRenderingStageView( new Carna::presets::OpaqueRenderingStage( geometryType ) )
{
}



// ----------------------------------------------------------------------------------
// VolumeRenderingStageView
// ----------------------------------------------------------------------------------

const unsigned int VolumeRenderingStageView::DEFAULT_SAMPLE_RATE = Carna::presets::VolumeRenderingStage::DEFAULT_SAMPLE_RATE;


VolumeRenderingStageView::VolumeRenderingStageView( Carna::presets::VolumeRenderingStage* renderStage )
    : RenderStageView::RenderStageView( renderStage )
{
}


Carna::presets::VolumeRenderingStage& VolumeRenderingStageView::volumeRenderingStage()
{
    return static_cast< Carna::presets::VolumeRenderingStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// MaskRenderingStageView
// ----------------------------------------------------------------------------------

MaskRenderingStageView::MaskRenderingStageView( unsigned int geometryType, unsigned int maskRole )
    : VolumeRenderingStageView::VolumeRenderingStageView(
        new Carna::presets::MaskRenderingStage( geometryType, maskRole )
    )
{
}


Carna::presets::MaskRenderingStage& MaskRenderingStageView::maskRenderingStage()
{
    return static_cast< Carna::presets::MaskRenderingStage& >( *renderStage );
}



// ----------------------------------------------------------------------------------
// MIPLayerView
// ----------------------------------------------------------------------------------

MIPLayerView::~MIPLayerView()
{
    if( !ownedBy )
    {
        delete mipLayer;
    }
}



// ----------------------------------------------------------------------------------
// MIPStageView
// ----------------------------------------------------------------------------------

const static auto MIP_STAGE__ROLE_INTENSITIES = Carna::presets::MIPStage::ROLE_INTENSITIES;


MIPStageView::MIPStageView( unsigned int geometryType )
    : VolumeRenderingStageView::VolumeRenderingStageView(
        new Carna::presets::MIPStage( geometryType )
    )
{
}


Carna::presets::MIPStage& MIPStageView::mipStage()
{
    return static_cast< Carna::presets::MIPStage& >( *renderStage );
}


void MIPStageView::appendLayer( MIPLayerView* mipLayerView )
{
    if( mipLayerView->ownedBy )
    {
        mipLayerView->ownedBy->removeLayer( *mipLayerView );
    }
    mipLayerView->ownedBy = std::static_pointer_cast< MIPStageView >( this->shared_from_this() );
    mipStage().appendLayer( mipLayerView->mipLayer );
}


void MIPStageView::removeLayer( MIPLayerView& mipLayerView )
{
    mipLayerView.ownedBy.reset();
    mipStage().removeLayer( *( mipLayerView.mipLayer ) );
}



// ----------------------------------------------------------------------------------
// CuttingPlanesStageView
// ----------------------------------------------------------------------------------

const static auto CUTTING_PLANES_STAGE__ROLE_INTENSITIES = Carna::presets::CuttingPlanesStage::ROLE_INTENSITIES;


CuttingPlanesStageView::CuttingPlanesStageView( unsigned int volumeGeometryType, unsigned int planeGeometryType )
    : RenderStageView::RenderStageView(
        new Carna::presets::CuttingPlanesStage( volumeGeometryType, planeGeometryType )
    )
{
}


Carna::presets::CuttingPlanesStage& CuttingPlanesStageView::cuttingPlanesStage()
{
    return static_cast< Carna::presets::CuttingPlanesStage& >( *renderStage );
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
        .doc() = R"(Implements rendering stage that renders opaque meshes.

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
        .def_readonly_static( "DEFAULT_ROLE_MASK", &Carna::presets::MaskRenderingStage::DEFAULT_ROLE_MASK )
        .def_readonly_static( "DEFAULT_COLOR", &Carna::presets::MaskRenderingStage::DEFAULT_COLOR )
        .def(
            py::init< unsigned int, unsigned int >(),
            "geometry_type"_a, "mask_role"_a = Carna::presets::MaskRenderingStage::DEFAULT_ROLE_MASK
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
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().setColor( color ), const Carna::base::Color& color )
        )
        .def_property(
            "render_borders",
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().renderBorders() ),
            VIEW_DELEGATE( MaskRenderingStageView, maskRenderingStage().setRenderBorders( renderBorders ), bool renderBorders )
        )
        .doc() = R"(Renders 3D masks.

        .. literalinclude:: ../test/test_integration.py
           :start-after: # .. MaskRenderingStage: example-setup-start
           :end-before: # .. MaskRenderingStage: example-setup-end
           :dedent: 8

        Rendering the scene as an animation:

        .. image:: ../test/results/expected/test_integration.MaskRenderingStage.test__animated.png
           :width: 400)";

    /* MIPLayer
     */
    py::class_< MIPLayerView, std::shared_ptr< MIPLayerView > >( m, "MIPLayer" )
        .def( py::init< float, float, const Carna::base::Color& >(), "min_intensity"_a, "max_intensity"_a, "color"_a );
    
    /* MIPStage
     */
    py::class_< MIPStageView, std::shared_ptr< MIPStageView >, VolumeRenderingStageView >( m, "MIPStage" )
        .def_readonly_static( "ROLE_INTENSITIES", &MIP_STAGE__ROLE_INTENSITIES )
        .def( py::init< unsigned int >(), "geometry_type"_a )
        .def( "append_layer", &MIPStageView::appendLayer, "layer"_a )
        .def( "remove_layer", &MIPStageView::removeLayer, "layer"_a )
        .doc() = R"(Renders maximum intensity projections of volume geometries in the scene.

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
        .def_readonly_static( "DEFAULT_WINDOWING_WIDTH", &Carna::presets::CuttingPlanesStage::DEFAULT_WINDOWING_WIDTH )
        .def_readonly_static( "DEFAULT_WINDOWING_LEVEL", &Carna::presets::CuttingPlanesStage::DEFAULT_WINDOWING_LEVEL )
        .def( py::init< unsigned int, unsigned int >(), "volume_geometry_type"_a, "plane_geometry_type"_a )
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
        .doc() = R"(Renders cutting planes of volume geometries in the scene.

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

    py::class_< VolumeRenderingStage, RenderStage >( m, "VolumeRenderingStage" )
        .def_property( "sample_rate", &VolumeRenderingStage::sampleRate, &VolumeRenderingStage::setSampleRate );

    const static auto MIPLayer__LAYER_FUNCTION_ADD     = ([](){ return MIPLayer::LAYER_FUNCTION_ADD;     })();
    const static auto MIPLayer__LAYER_FUNCTION_REPLACE = ([](){ return MIPLayer::LAYER_FUNCTION_REPLACE; })();

    py::class_< DVRStage, VolumeRenderingStage >( m, "DVRStage" )
        .def_static( "create", []( unsigned int geometryType )
        {
            return new DVRStage( geometryType );
        }
        , py::return_value_policy::reference, "geometryType"_a )
        .def_property_readonly_static( "DEFAULT_TRANSLUCENCY", []( py::object ) { return DVRStage::DEFAULT_TRANSLUCENCE; } )
        .def_property_readonly_static( "DEFAULT_DIFFUSE_LIGHT", []( py::object ) { return DVRStage::DEFAULT_DIFFUSE_LIGHT; } )
        .def_property_readonly_static( "ROLE_INTENSITIES", []( py::object ) { return DVRStage::ROLE_INTENSITIES; } )
        .def_property_readonly_static( "ROLE_NORMALS", []( py::object ) { return DVRStage::ROLE_NORMALS; } )
        .def_property( "translucency", &DVRStage::translucence, &DVRStage::setTranslucence )
        .def_property( "diffuse_light", &DVRStage::diffuseLight, &DVRStage::setDiffuseLight )
        .def( "clear_color_map", &DVRStage::clearColorMap )
        .def( "write_color_map", []( DVRStage* self, float min, float max, const math::Vector4f& color1, const math::Vector4f& color2 )
        {
            self->writeColorMap( min, max, color1, color2 );
        }
        , "min"_a, "max"_a, "color1"_a, "color2"_a );
*/

}