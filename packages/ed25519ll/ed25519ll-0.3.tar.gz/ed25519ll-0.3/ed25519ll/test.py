# -*- coding: utf-8 -*-

from nose.tools import raises
import ed25519ll 

def test_ed25519ll():
    msg = b"The rain in Spain stays mainly on the plain"
    kp = ed25519ll.crypto_sign_keypair()
    signed = ed25519ll.crypto_sign(msg, kp.sk)    
    
    @raises(ValueError)
    def open_corrupt(): 
        corrupt = signed[ed25519ll.SIGNATUREBYTES:] + b'U' + signed[ed25519ll.SIGNATUREBYTES+1:]
        ed25519ll.crypto_sign_open(corrupt, kp.vk)                
    open_corrupt()
    
    @raises(AssertionError)
    def short_sk():
        signed = ed25519ll.crypto_sign(msg, kp.sk[:-1])
    short_sk()
    
    ed25519ll.crypto_sign_open(signed, kp.vk)
    
def test_cover_warn_seed():
    ed25519ll.crypto_sign_keypair(b'*'*32)
    
@raises(ValueError)
def test_bad_seed_size():
    ed25519ll.crypto_sign_keypair(b'*'*31)

if __name__ == "__main__":
    test_ed25519ll()
