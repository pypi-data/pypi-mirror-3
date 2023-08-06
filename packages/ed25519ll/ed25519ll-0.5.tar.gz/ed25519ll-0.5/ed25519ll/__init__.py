# -*- coding: utf-8 -*-

import warnings
import os
import os.path
import pkg_resources
from collections import namedtuple
from distutils import sysconfig
from distutils.util import get_platform
import ctypes

__all__ = ['crypto_sign', 'crypto_sign_open', 'crypto_sign_keypair', 'Keypair',
           'PUBLICKEYBYTES', 'SECRETKEYBYTES', 'SIGNATUREBYTES']

plat_name = get_platform().replace('-', '_')
so_suffix = sysconfig.get_config_var('SO')
lib_filename = '_ed25519_%s%s' % (plat_name, so_suffix)

_ed25519 = ctypes.cdll.LoadLibrary(
        os.path.abspath(os.path.join(os.path.dirname(__file__), lib_filename)))

PUBLICKEYBYTES=32
SECRETKEYBYTES=64
SIGNATUREBYTES=64
    
Keypair = namedtuple('Keypair', ('vk', 'sk')) # verifying key, secret key

def crypto_sign_keypair(seed=None):
    """Return (verifying, secret) key from a given seed, or os.urandom(32)"""
    vk = ctypes.create_string_buffer(PUBLICKEYBYTES)
    sk = ctypes.create_string_buffer(SECRETKEYBYTES)
    if seed is None:
        seed = os.urandom(PUBLICKEYBYTES)
    else:
        warnings.warn("ed25519ll should choose random seed.",
                      RuntimeWarning)
    if len(seed) != 32:
        raise ValueError("seed must be 32 random bytes or None.")
    s = ctypes.c_char_p(seed)
    rc = _ed25519.crypto_sign_keypair(vk, sk, s)
    if rc != 0: # pragma no cover (no other return statement in C)
        raise ValueError("rc != 0", rc)
    return Keypair(vk.raw, sk.raw)


def crypto_sign(msg, sk):
    """Return signature+message given message and secret key.
    The signature is the first SIGNATUREBYTES bytes of the return value.
    A copy of msg is in the remainder."""
    assert len(sk) == SECRETKEYBYTES, len(sk)
    sk = ctypes.create_string_buffer(sk, SECRETKEYBYTES) # const
    m = ctypes.create_string_buffer(msg, len(msg)) # const
    sig_and_msg = ctypes.create_string_buffer(len(msg) + SIGNATUREBYTES) # out
    sig_and_msg_len = ctypes.c_ulonglong() # out
    rc = _ed25519.crypto_sign(sig_and_msg,
                              ctypes.byref(sig_and_msg_len),
                              m, ctypes.c_ulonglong(len(m)),
                              sk)
    if rc != 0: # pragma no cover (no other return statement in C)
        raise ValueError("rc != 0", rc)
    return sig_and_msg.raw[:sig_and_msg_len.value]


def crypto_sign_open(signed, vk):
    """Return message given signature+message and the verifying key."""
    assert len(vk) == PUBLICKEYBYTES
    sm = ctypes.create_string_buffer(signed, len(signed)) # const
    vk = ctypes.create_string_buffer(vk, len(vk)) # const
    newmsg = ctypes.create_string_buffer(len(signed)) # out
    newmsg_len = ctypes.c_ulonglong() # out
    rc = _ed25519.crypto_sign_open(newmsg, ctypes.byref(newmsg_len), 
                                   sm, len(sm), vk)
    if rc != 0:
        raise ValueError("rc != 0", rc)    
    return newmsg.raw[:newmsg_len.value]

