#include <Carna/py/Log.h>

using namespace Carna::py;



// ----------------------------------------------------------------------------------
// NullWriter
// ----------------------------------------------------------------------------------

void NullWriter::writeLine( Carna::base::Log::Severity, const std::string& ) const
{
}