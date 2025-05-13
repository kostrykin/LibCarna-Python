#define EGL_EGLEXT_PROTOTYPES

#include <LibCarna/base/glew.hpp>
#include <LibCarna/egl/EGLContext.hpp>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <cstdlib>
#include <unordered_set>

// see: https://developer.nvidia.com/blog/egl-eye-opengl-visualization-without-x-server/



// ----------------------------------------------------------------------------------
// REPORT_EGL_ERROR
// ----------------------------------------------------------------------------------

#ifndef NO_EGL_ERROR_CHECKING

    #include <LibCarna/base/LibCarnaException.hpp>

    #define REPORT_EGL_ERROR { \
            const unsigned int err = eglGetError(); \
            LIBCARNA_ASSERT_EX( err == EGL_SUCCESS, "EGL Error State in " \
                << __func__ \
                << " [" << err << "] (" << __FILE__ << ":" << __LINE__ << ")" ); }
#else

    #define REPORT_EGL_ERROR

#endif



// ----------------------------------------------------------------------------------
// CONFIG_ATTRIBS
// ----------------------------------------------------------------------------------

static const EGLint CONFIG_ATTRIBS[] =
{
    EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
    EGL_BLUE_SIZE, 8,
    EGL_GREEN_SIZE, 8,
    EGL_RED_SIZE, 8,
    EGL_DEPTH_SIZE, 8,
    EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
    EGL_NONE
};



// ----------------------------------------------------------------------------------
// PBUFFER_ATTRIBS
// ----------------------------------------------------------------------------------

static const EGLint PBUFFER_ATTRIBS[] =
{
    EGL_WIDTH, 0,
    EGL_HEIGHT, 0,
    EGL_NONE
};



// ----------------------------------------------------------------------------------
// LibCarna :: egl :: EGLContext :: Details
// ----------------------------------------------------------------------------------

struct LibCarna::egl::EGLContext::Details
{
    ::EGLDisplay eglDpy;
    ::EGLSurface eglSurf;
    ::EGLContext eglCtx;

    std::string vendor;
    std::string renderer;

    void selectDisplay();
    bool initializeDisplay();
    void activate() const;
};


bool LibCarna::egl::EGLContext::Details::initializeDisplay()
{
    EGLint major, minor;
    const EGLBoolean initialize = eglInitialize( eglDpy, &major, &minor );
    return initialize == EGL_TRUE;
}


void LibCarna::egl::EGLContext::Details::selectDisplay()
{
    eglDpy = eglGetDisplay( EGL_DEFAULT_DISPLAY );
    if( eglDpy == EGL_NO_DISPLAY || !initializeDisplay() )
    {
        LibCarna::base::Log::instance().record( LibCarna::base::Log::warning, "EGL_DEFAULT_DISPLAY initialization failed" );

        /* Load EGL extensions.
         */
        PFNEGLQUERYDEVICESEXTPROC eglQueryDevicesEXT = ( PFNEGLQUERYDEVICESEXTPROC ) eglGetProcAddress("eglQueryDevicesEXT");
        PFNEGLGETPLATFORMDISPLAYEXTPROC eglGetPlatformDisplayEXT = ( PFNEGLGETPLATFORMDISPLAYEXTPROC ) eglGetProcAddress("eglGetPlatformDisplayEXT");

        /* Query EGL devices.
         */
        const static int MAX_DEVICES = 8;
        EGLDeviceEXT eglDevices[ MAX_DEVICES ];
        EGLint numDevices;
        eglQueryDevicesEXT( MAX_DEVICES, eglDevices, &numDevices );

        std::stringstream msg;
        msg << numDevices << " EGL device(s) found";
        LibCarna::base::Log::instance().record( LibCarna::base::Log::debug, msg.str() );

        /* Try to get displays from the devices.
         */
        for( unsigned int deviceIndex = 0; deviceIndex < numDevices; ++deviceIndex )
        {
            eglDpy = eglGetPlatformDisplayEXT( EGL_PLATFORM_DEVICE_EXT,  eglDevices[ deviceIndex ], 0 );
            if( eglDpy != EGL_NO_DISPLAY && initializeDisplay() )
            {
                std::stringstream msg;
                msg << "Successfully initialized EGL display from device " << deviceIndex;
                LibCarna::base::Log::instance().record( LibCarna::base::Log::debug, msg.str() );
                break;
            }
        }
    }
}


void LibCarna::egl::EGLContext::Details::activate() const
{
    eglMakeCurrent( this->eglDpy, this->eglSurf, this->eglSurf, this->eglCtx );
    REPORT_EGL_ERROR;
}



// ----------------------------------------------------------------------------------
// LibCarna :: egl :: EGLContext
// ----------------------------------------------------------------------------------

static std::unordered_set< LibCarna::egl::EGLContext* > eglContextInstances;


LibCarna::egl::EGLContext::EGLContext( Details* _pimpl )
    : LibCarna::base::GLContext( false )
    , pimpl( _pimpl ) // TODO: rename to `pimpl`
{
    eglContextInstances.insert( this );
}


LibCarna::egl::EGLContext* LibCarna::egl::EGLContext::create()
{
    using EGLContext = ::EGLContext;
    unsetenv( "DISPLAY" ); // see https://stackoverflow.com/q/67885750/1444073

    Details* const pimpl = new Details();
    pimpl->selectDisplay();
    LIBCARNA_ASSERT( pimpl->eglDpy != EGL_NO_DISPLAY );

    eglBindAPI( EGL_OPENGL_API );
    REPORT_EGL_ERROR;

    EGLint numConfigs;
    EGLConfig eglCfg;
    const EGLBoolean chooseConfig = eglChooseConfig( pimpl->eglDpy, CONFIG_ATTRIBS, &eglCfg, 1, &numConfigs );
    LIBCARNA_ASSERT( chooseConfig == EGL_TRUE );

    pimpl->eglSurf = eglCreatePbufferSurface( pimpl->eglDpy, eglCfg, PBUFFER_ATTRIBS );
    LIBCARNA_ASSERT( pimpl->eglSurf != EGL_NO_SURFACE );

    const ::EGLContext shareContext = eglContextInstances.empty() ? EGL_NO_CONTEXT : ( *eglContextInstances.begin() )->pimpl->eglCtx;
    pimpl->eglCtx = eglCreateContext( pimpl->eglDpy, eglCfg, shareContext, NULL );
    LIBCARNA_ASSERT( pimpl->eglCtx != EGL_NO_CONTEXT );

    pimpl->activate();
    REPORT_EGL_ERROR;

    pimpl->vendor   = ( const char* ) glGetString( GL_VENDOR   );
    pimpl->renderer = ( const char* ) glGetString( GL_RENDERER );
    REPORT_EGL_ERROR;

    return new LibCarna::egl::EGLContext( pimpl );
}


LibCarna::egl::EGLContext::~EGLContext()
{
    eglContextInstances.erase( this );
    eglDestroyContext( pimpl->eglDpy, pimpl->eglCtx );
    eglDestroySurface( pimpl->eglDpy, pimpl->eglSurf );
}


void LibCarna::egl::EGLContext::activate() const
{
    pimpl->activate();
}


const std::string& LibCarna::egl::EGLContext::vendor() const
{
    return pimpl->vendor;
}


const std::string& LibCarna::egl::EGLContext::renderer() const
{
    return pimpl->renderer;
}
