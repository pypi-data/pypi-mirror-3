import pkg_resources
import sysconfig
import os.path
import glob

from distutils.util import get_platform
from cffi import FFI
from distutils.extension import Extension
ffi = FFI()

decl = """
    extern int crypto_sign(unsigned char *, unsigned long long *,
        const unsigned char *, unsigned long long, const unsigned char *);
    
    extern int crypto_sign_open(unsigned char *, unsigned long long *, 
        const unsigned char *, unsigned long long, const unsigned char *);
    
    extern int crypto_sign_keypair(unsigned char *pk, unsigned char *sk, 
        unsigned char *seed);
"""

ffi.cdef(decl)

verify = True

plat_name = get_platform().replace('-', '_')
so_suffix = sysconfig.get_config_var('SO')
library_dir = os.path.abspath(pkg_resources.resource_filename('ed25519ll', ''))
if not verify: # pragma no cover
    lib_filename = pkg_resources.resource_filename('ed25519ll', 
                                                   '_ed25519_%s%s' %
                                                   (plat_name, so_suffix))
    _ed25519 = ffi.dlopen(os.path.abspath(lib_filename))
else:
    so_prefix = ""
    if os.name == "posix":
        so_prefix = ":" # to link with libraries without 'lib' prefix
    _ed25519 = ffi.verify(decl,
                          libraries=["%s_ed25519_%s%s" % (so_prefix,
                                                          plat_name,
                                                          so_suffix)],
                          library_dirs=[library_dir],
                          export_symbols=["crypto_sign",
                                          "crypto_sign_open",
                                          "crypto_sign_keypair"],
                          )

crypto_sign_keypair = _ed25519.crypto_sign_keypair
crypto_sign = _ed25519.crypto_sign
crypto_sign_open = _ed25519.crypto_sign_open
