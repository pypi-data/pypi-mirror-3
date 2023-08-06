#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
import os
import os.path
import pkg_resources
from distutils.util import get_platform
from collections import namedtuple
try:
    import sysconfig
except ImportError: # pragma no cover
    from distutils import sysconfig
    
__all__ = ['crypto_sign', 'crypto_sign_open', 'crypto_sign_keypair', 'Keypair',
           'PUBLICKEYBYTES', 'SECRETKEYBYTES', 'SIGNATUREBYTES']

from cffi import FFI
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

verify = False

if not verify:    
    plat_name = get_platform().replace('-', '_')
    so_suffix = sysconfig.get_config_var('SO')
    lib_filename = pkg_resources.resource_filename('ed25519ll', '_ed25519_%s%s' %
                                                   (plat_name, so_suffix))
    _ed25519 = ffi.dlopen(os.path.abspath(lib_filename))
else: # pragma no cover
    # set LIBRARY_PATH to pwd or use -L
    _ed25519 = ffi.verify(decl, libraries=["ed25519"]) # library_dirs = []

PUBLICKEYBYTES=32
SECRETKEYBYTES=64
SIGNATUREBYTES=64

def _ffi_tobytes(c, size):
    return bytes(ffi.buffer(c, size))

Keypair = namedtuple('Keypair', ('vk', 'sk')) # verifying key, secret key

def crypto_sign_keypair(seed=None):
    """Return (verifying, secret) key from a given seed, or os.urandom(32)"""
    pk = ffi.new('unsigned char[32]')
    sk = ffi.new('unsigned char[64]')
    if seed is None:
        seed = os.urandom(PUBLICKEYBYTES)
    else:
        warnings.warn("ed25519ll should choose random seed.",
                      RuntimeWarning)
    if len(seed) != 32:
        raise ValueError("seed must be 32 random bytes or None.")
    s = ffi.new('unsigned char[32]', map(ord, seed))
    rc = _ed25519.crypto_sign_keypair(pk, sk, s)
    if rc != 0: # pragma no cover (no other return statement in C)
        raise ValueError("rc != 0", rc)
    return Keypair(_ffi_tobytes(pk, len(pk)), _ffi_tobytes(sk, len(sk)))


def crypto_sign(msg, sk):
    """Return signature+message given message and secret key.
    The signature is the first SIGNATUREBYTES bytes of the return value.
    A copy of msg is in the remainder."""
    assert len(sk) == SECRETKEYBYTES
    sk = ffi.new('unsigned char[]', map(ord, sk))
    m = ffi.new('unsigned char[]', map(ord, msg))
    sig_and_msg = ffi.new('unsigned char[]', (len(msg) + SIGNATUREBYTES))
    sig_and_msg_len = ffi.new('unsigned long long')
    rc = _ed25519.crypto_sign(sig_and_msg, sig_and_msg_len, m, len(m), sk)
    if rc != 0: # pragma no cover (no other return statement in C)
        raise ValueError("rc != 0", rc)
    return _ffi_tobytes(sig_and_msg, sig_and_msg_len[0])


def crypto_sign_open(signed, vk):
    """Return message given signature+message and the verifying key."""
    assert len(vk) == PUBLICKEYBYTES    
    sm = ffi.new('unsigned char[]', map(ord, signed))
    vk = ffi.new('unsigned char[]', map(ord, vk))
    newmsg = ffi.new('unsigned char[]', len(signed))
    newmsg_len = ffi.new('unsigned long long') # a pointer
    rc = _ed25519.crypto_sign_open(newmsg, newmsg_len, sm, len(sm), vk)
    if rc != 0:
        raise ValueError("rc != 0", rc)    
    return _ffi_tobytes(newmsg, newmsg_len[0])

