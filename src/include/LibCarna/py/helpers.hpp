#pragma once

#include <LibCarna/LibCarna.hpp>
#include <LibCarna/py/base.hpp>

namespace LibCarna
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

    std::vector< std::shared_ptr< LibCarna::py::base::RenderStageView > > stages;

public:

    FrameRendererHelperView( const std::shared_ptr< LibCarna::py::base::FrameRendererView >& frameRendererView );

    const std::shared_ptr< LibCarna::py::base::FrameRendererView > frameRendererView;

    void add_stage( const std::shared_ptr< LibCarna::py::base::RenderStageView >& stage );

    void commit();

    void reset();

}; // FrameRendererHelperView



}  // namespace LibCarna :: py :: helpers

}  // namespace LibCarna :: py

}  // namespace LibCarna