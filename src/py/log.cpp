#include <LibCarna/py/log.hpp>

using namespace LibCarna::py;



// ----------------------------------------------------------------------------------
// NullWriter
// ----------------------------------------------------------------------------------

void NullWriter::writeLine( LibCarna::base::Log::Severity, const std::string& ) const
{
}