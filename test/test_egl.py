import carna.egl

import faulthandler
faulthandler.enable()


print('--- test begin ---')
ctx = carna.egl.Context.create()
del ctx
print('--- test end ---')