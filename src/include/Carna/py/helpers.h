#pragma once

#include <Carna/Carna.h>
#include <Carna/py/base.h>

namespace Carna
{

namespace py
{

namespace helpers
{



// ----------------------------------------------------------------------------------
// FrameRendererHelperView
// ----------------------------------------------------------------------------------

class FrameRendererHelperView
{

    std::vector< std::shared_ptr< Carna::py::base::RenderStageView > > stages;

public:

    FrameRendererHelperView( const std::shared_ptr< Carna::py::base::FrameRendererView >& frameRendererView );

    const std::shared_ptr< Carna::py::base::FrameRendererView > frameRendererView;

    void add_stage( const std::shared_ptr< Carna::py::base::RenderStageView >& stage );

    void commit();

    void reset();

}; // FrameRendererHelperView



}  // namespace Carna :: py :: helpers

}  // namespace Carna :: py

}  // namespace Carna