#pragma once

#include <LibCarna/base/Log.hpp>

namespace LibCarna
{

namespace py
{



// ----------------------------------------------------------------------------------
// NullWriter
// ----------------------------------------------------------------------------------

class NullWriter : public LibCarna::base::Log::TextWriter
{

public:

    virtual void writeLine( LibCarna::base::Log::Severity, const std::string& ) const override;

}; // NullWriter



}  // namespace LibCarna :: py

}  // namespace LibCarna

