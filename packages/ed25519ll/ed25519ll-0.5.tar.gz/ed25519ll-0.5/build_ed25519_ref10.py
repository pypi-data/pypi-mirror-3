#!/usr/bin/env python
# obsolete

import glob
import os
import os.path
import platformer
import distutils.util

plat_name = distutils.util.get_platform().replace('-', '_')
output = os.path.abspath(os.path.join('ed25519ll', '_ed25519_%s' % plat_name))
os.chdir("ed25519-supercop-ref10")
platformer.platform.compile(glob.glob("*.c"), 
        platformer.ExternalCompilationInfo(compile_extra=['-march=native']), 
        outputfilename=output, standalone=False)
