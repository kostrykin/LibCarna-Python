#pragma once

#include <Carna/base/Log.h>

namespace Carna
{

namespace py
{



// ----------------------------------------------------------------------------------
// NullWriter
// ----------------------------------------------------------------------------------

class NullWriter : public Carna::base::Log::TextWriter
{

public:

    virtual void writeLine( Carna::base::Log::Severity, const std::string& ) const override;

}; // NullWriter



}  // namespace Carna :: py

}  // namespace Carna

