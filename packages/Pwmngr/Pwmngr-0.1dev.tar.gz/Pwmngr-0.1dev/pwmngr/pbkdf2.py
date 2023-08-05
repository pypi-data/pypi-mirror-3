# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Florent D'halluin <flal@melix.net> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------


# a pbkdf2 ( http://tools.ietf.org/html/rfc2898 ) implementation in python .

#   this awesome algorithm allows you to derive a key of desired lenght (in bytes)
#   from a given password and hash 

import hashlib
import struct 

h = hashlib.sha1

def hmac_sha1(k,msg) :
    bsize = 64 
    if len(k) > bsize :
        k = h(k).digest()
    if( len(k) < bsize) :
        k = k + chr(0)*(bsize  - len(k))
    o = b''.join([chr(ord(x) ^ 0x5c) for x in k])
    i = b''.join([chr(ord(x) ^ 0x36) for x in k])
    hi = h()
    hi.update(i)
    hi.update(msg)
    di = hi.digest()
    hr = h(o)
    hr.update(di)
    #print hr.hexdigest()
    return hr.digest()
    

def xorImpl(b1,b2) :
    """ bitwise xor on two arrays of bytes """
    res = b''.join([chr(ord(a)^ord(b)) for a,b in zip(b1,b2)])
    return res
    
    

def pbkdf2(pwd, salt=bytes("salt"), c=1024, target_len = 32):
    """
    c : number of rounds 
    target_len : in bytes default to 32bytes (256bits) 
    """
    hlen = h().digest_size
    r = target_len % hlen # how many bytes to keep from last round
    if(r) :
        l = target_len / hlen + 1
    else :
        l = target_len / hlen
    blocks= []
    for i in xrange(l) :
        num = struct.pack('>I',i+1)
        u = hmac_sha1(pwd, salt + num)
        block = u
        for j in xrange(c-1) :
            u = hmac_sha1(pwd,u)
            block = xorImpl(block,u)
        blocks.append(block)

    # truncate the last block to get the right size
    if(r) :
        blocks[-1] = blocks[-1][:r]
    derived_key = b''.join(blocks)
    return derived_key
    
        
if __name__ == '__main__':
    keytest = pbkdf2(b'password',b'salt',c=1,target_len=20)
    hkeytest = [hex(ord(b)) for b in keytest]
    assert(hkeytest[0] == '0xc')
    assert(hkeytest[-1] == '0xa6')
    keytest = pbkdf2(b'password',b'salt',c=4096,target_len=20)
    hkeytest = [hex(ord(b)) for b in keytest]
    assert(hkeytest[0] == '0x4b')
    assert(hkeytest[-1] == '0xc1')
    
