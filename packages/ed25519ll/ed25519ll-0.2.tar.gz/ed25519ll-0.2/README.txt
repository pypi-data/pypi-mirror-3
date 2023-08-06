About Ed25519
=============

Ed25519 is a public-key signature system with several attractive features 
including:

* Fast single-signature verification.
* Very fast signing.
* Fast key generation.
* High security level.
* Small signatures. Signatures fit into 64 bytes.
* Small keys. Public keys consume only 32 bytes. 

This text abridged from http://ed25519.cr.yp.to/.

About ed25519ll
===============

ed25519ll is a low-level cffi wrapper for the Ed25519 public key signature
system. It uses distutils' Extension() to compile a shared library that is not 
a Python extension module, and then uses cffi to talk to the library.

This wrapper currently exposes only the slow reference implmentation of Ed25519, 
on my 2.6GHz Athlon achieving about 380 signatures/second/core including the wrapper 
overhead.

Example::
    
    import ed25519ll
    msg = b"The rain in Spain stays mainly on the plain"
    kp = ed25519ll.crypto_sign_keypair()
    signed = ed25519ll.crypto_sign(msg, kp.sk) 
    verified = ed25519ll.crypto_sign_open(signed, kp.vk)
    assert verified == msg  # but ValueError is raised for bad signatures 
