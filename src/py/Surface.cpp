#include <LibCarna/py/Surface.hpp>
#include <LibCarna/base/Framebuffer.hpp>
#include <LibCarna/base/GLContext.hpp>
#include <LibCarna/base/Texture.hpp>
#include <LibCarna/base/glew.hpp>

namespace LibCarna
{

namespace py
{



// ----------------------------------------------------------------------------------
// createRenderTexture
// ----------------------------------------------------------------------------------

static LibCarna::base::Texture< 2 >* createRenderTexture( const LibCarna::base::GLContext& glContext )
{
    glContext.makeCurrent();
    return LibCarna::base::Framebuffer::createRenderTexture();
}



// ----------------------------------------------------------------------------------
// Surface :: Details
// ----------------------------------------------------------------------------------

struct Surface::Details
{
    Details( const LibCarna::base::GLContext& glContext, unsigned int width, unsigned int height );

    const LibCarna::base::GLContext& glContext;
    const std::size_t frameSize;
    const std::unique_ptr< unsigned char[] > frame;
    const std::unique_ptr< LibCarna::base::Texture< 2 > > renderTexture;
    const std::unique_ptr< LibCarna::base::Framebuffer > fbo;
    std::unique_ptr< LibCarna::base::Framebuffer::Binding > fboBinding;

    void grabFrame();
};


Surface::Details::Details( const LibCarna::base::GLContext& glContext, unsigned int width, unsigned int height )
    : glContext( glContext )
    , frameSize( width * height * 3 )
    , frame( new unsigned char[ frameSize ] )
    , renderTexture( createRenderTexture( glContext ) )
    , fbo( new LibCarna::base::Framebuffer( width, height, *renderTexture ) )
{
}


void Surface::Details::grabFrame()
{
    glContext.makeCurrent();

    glReadBuffer( GL_COLOR_ATTACHMENT0_EXT );
    glReadPixels( 0, 0, this->fbo->width(), this->fbo->height(), GL_RGB, GL_UNSIGNED_BYTE, frame.get() );
}



// ----------------------------------------------------------------------------------
// Surface
// ----------------------------------------------------------------------------------

Surface::Surface( const LibCarna::py::base::GLContextView& contextView, unsigned int width, unsigned int height )
    : pimpl( new Details( *contextView.context, width, height ) )
    , contextView( contextView.shared_from_this() )
    , size( pimpl->frameSize )
{
}


Surface::~Surface()
{
    pimpl->glContext.makeCurrent();
}


unsigned int Surface::width() const
{
    return pimpl->fbo->width();
}


unsigned int Surface::height() const
{
    return pimpl->fbo->height();
}


void Surface::begin() const
{
    pimpl->glContext.makeCurrent();
    pimpl->fboBinding.reset( new LibCarna::base::Framebuffer::Binding( *pimpl->fbo ) );
}


pybind11::array_t< unsigned char > Surface::end() const
{
    pimpl->grabFrame();
    pimpl->fboBinding.reset();
    const unsigned char* const pixelData = pimpl->frame.get();

    pybind11::buffer_info buf; // performs flipping
    buf.itemsize = sizeof( unsigned char );
    buf.format   = pybind11::format_descriptor< unsigned char >::value;
    buf.ndim     = 3;
    buf.shape    = { height(), width(), 3 };
    buf.strides  = { -buf.itemsize * 3 * width(), buf.itemsize * 3, buf.itemsize };
    buf.ptr      = const_cast< unsigned char* >( pixelData ) + buf.itemsize * 3 * width() * ( height() - 1 );
    return pybind11::array( buf );
}



}  // namespace LibCarna :: py

}  // namespace LibCarna

