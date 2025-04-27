#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

using namespace pybind11::literals; // enables the _a literal

#include <Carna/base/GLContext.h>
#include <Carna/base/Color.h>
#include <Carna/presets/MaskRenderingStage.h>
#include <Carna/py/presets.h>
/*
#include <Carna/base/GLContext.h>
#include <Carna/base/ManagedMesh.h>
#include <Carna/presets/CuttingPlanesStage.h>
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
           :start-after: # .. OpaqueRenderingStage: example-start
           :end-before: # .. OpaqueRenderingStage: example-end
           :dedent: 8

        This is the image ``array`` rendered in the example:

        .. image:: ../test/results/expected/test_integration.OpaqueRenderingStage.test.png
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
           :start-after: # .. MaskRenderingStage: example-start
           :end-before: # .. MaskRenderingStage: example-end
           :dedent: 8

        This is the image ``array`` rendered in the example:

        .. image:: ../test/results/expected/test_integration.MaskRenderingStage.test.png
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

    py::class_< MIPLayer >( m, "MIPLayer" )
        .def_static( "create", []( float min, float max, const math::Vector4f& color, const BlendFunction& function )
        {
            return new MIPLayer( min, max, color, function );
        }
        , py::return_value_policy::reference, "min"_a, "max"_a, "color"_a, "function"_a = MIPLayer__LAYER_FUNCTION_REPLACE )
        .def_readonly_static( "LAYER_FUNCTION_ADD", &MIPLayer__LAYER_FUNCTION_ADD )
        .def_readonly_static( "LAYER_FUNCTION_REPLACE", &MIPLayer__LAYER_FUNCTION_REPLACE )
        .DEF_FREE( MIPLayer );

    py::class_< MIPStage, VolumeRenderingStage >( m, "MIPStage" )
        .def_static( "create", []( unsigned int geometryType )
        {
            return new MIPStage( geometryType );
        }
        , py::return_value_policy::reference, "geometryType"_a )
        .def_property_readonly_static( "ROLE_INTENSITIES", []( py::object ) { return MIPStage::ROLE_INTENSITIES; } )
        .def( "ascend_layer", &MIPStage::ascendLayer )
        .def( "append_layer", &MIPStage::appendLayer )
        .def( "remove_layer", &MIPStage::removeLayer )
        .def_property_readonly( "layers_count", &MIPStage::layersCount )
        .def( "layer", py::overload_cast< std::size_t >( &MIPStage::layer, py::const_ ) )
        .def( "clear_layers", &MIPStage::clearLayers );

    py::class_< CuttingPlanesStage, RenderStage >( m, "CuttingPlanesStage" )
        .def_static( "create", []( unsigned int volumeGeometryType, unsigned int planeGeometryType )
        {
            const auto cps = new CuttingPlanesStage( volumeGeometryType, planeGeometryType );
            CuttingPlanesStage__set_windowing( cps, 0.f, 1.f );
            return cps;
        }
        , py::return_value_policy::reference, "volumeGeometryType"_a, "planeGeometryType"_a )
        .def_property_readonly_static( "ROLE_INTENSITIES", []( py::object ) { return CuttingPlanesStage::ROLE_INTENSITIES; } )
        .def_property_readonly( "min_intensity", &CuttingPlanesStage::minimumIntensity )
        .def_property_readonly( "max_intensity", &CuttingPlanesStage::maximumIntensity )
        .def( "set_windowing", &CuttingPlanesStage__set_windowing )
        .def_property( "rendering_inverse", &CuttingPlanesStage::isRenderingInverse, &CuttingPlanesStage::setRenderingInverse );

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

    py::class_< MaskRenderingStage, VolumeRenderingStage >( m, "MaskRenderingStage" )
        .def_static( "create", []( unsigned int geometryType, unsigned int maskRole )
        {
            MaskRenderingStage* const mr = new MaskRenderingStage( geometryType, maskRole );
            mr->setRenderBorders( true );
            return mr;
        }
        , py::return_value_policy::reference, "geometryType"_a, "maskRole"_a = MaskRenderingStage::DEFAULT_ROLE_MASK )
        .def_readonly( "mask_role", &MaskRenderingStage::maskRole )
        .def_property_readonly_static( "DEFAULT_COLOR", []( py::object ) { return MaskRenderingStage::DEFAULT_COLOR; } )
        .def_property_readonly_static( "DEFAULT_ROLE_MASK", []( py::object ) { return MaskRenderingStage::DEFAULT_ROLE_MASK; } )
        .def_property
            ( "color"
            , []( MaskRenderingStage* self ) -> math::Vector4f
                {
                    return self->color();
                }
            , []( MaskRenderingStage* self, const math::Vector4f& color )
                {
                    self->setColor( color );
                }
            )
        .def_property( "render_borders", &MaskRenderingStage::renderBorders, &MaskRenderingStage::setRenderBorders );
*/

}