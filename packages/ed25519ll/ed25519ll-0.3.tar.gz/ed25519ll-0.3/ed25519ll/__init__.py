#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
import os
import os.path
import pkg_resources
from collections import namedtuple
from distutils import sysconfig

__all__ = ['crypto_sign', 'crypto_sign_open', 'crypto_sign_keypair', 'Keypair',
           'PUBLICKEYBYTES', 'SECRETKEYBYTES', 'SIGNATUREBYTES']

from . import _ed25519
ffi = _ed25519.ffi

PUBLICKEYBYTES=32
SECRETKEYBYTES=64
SIGNATUREBYTES=64

try: # Convert bytes (str) to a list of integers # pragma nocover 
    unicode
    def numlist(b):
        return map(ord, b)        
    def _ffi_tobytes(c, size):
        return ffi.buffer(c)[:size]
except NameError:
    def numlist(b):
        return list(b)
    def _ffi_tobytes(c, size):
        return ffi.buffer(c).tobytes()[:size]
    
Keypair = namedtuple('Keypair', ('vk', 'sk')) # verifying key, secret key

def crypto_sign_keypair(seed=None):
    """Return (verifying, secret) key from a given seed, or os.urandom(32)"""
    vk = ffi.new('unsigned char[32]')
    sk = ffi.new('unsigned char[64]')
    if seed is None:
        seed = os.urandom(PUBLICKEYBYTES)
    else:
        warnings.warn("ed25519ll should choose random seed.",
                      RuntimeWarning)
    if len(seed) != 32:
        raise ValueError("seed must be 32 random bytes or None.")
    s = ffi.new('unsigned char[32]', numlist(seed))
    rc = _ed25519.crypto_sign_keypair(vk, sk, s)
    if rc != 0: # pragma no cover (no other return statement in C)
        raise ValueError("rc != 0", rc)
    return Keypair(_ffi_tobytes(vk, 32), _ffi_tobytes(sk, 64))


def crypto_sign(msg, sk):
    """Return signature+message given message and secret key.
    The signature is the first SIGNATUREBYTES bytes of the return value.
    A copy of msg is in the remainder."""
    assert len(sk) == SECRETKEYBYTES
    sk = ffi.new('unsigned char[]', numlist(sk))
    m = ffi.new('unsigned char[]', numlist(msg))
    sig_and_msg = ffi.new('unsigned char[]', (len(msg) + SIGNATUREBYTES))
    sig_and_msg_len = ffi.new('unsigned long long[1]')
    rc = _ed25519.crypto_sign(sig_and_msg, sig_and_msg_len, m, len(m), sk)
    if rc != 0: # pragma no cover (no other return statement in C)
        raise ValueError("rc != 0", rc)
    return _ffi_tobytes(sig_and_msg, sig_and_msg_len[0])


def crypto_sign_open(signed, vk):
    """Return message given signature+message and the verifying key."""
    assert len(vk) == PUBLICKEYBYTES
    sm = ffi.new('unsigned char[]', numlist(signed))
    vk = ffi.new('unsigned char[]', numlist(vk))
    newmsg = ffi.new('unsigned char[]', len(signed))
    newmsg_len = ffi.new('unsigned long long[1]')
    rc = _ed25519.crypto_sign_open(newmsg, newmsg_len, sm, len(sm), vk)
    if rc != 0:
        raise ValueError("rc != 0", rc)    
    return _ffi_tobytes(newmsg, newmsg_len[0])

