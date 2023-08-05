#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Florent D'halluin <flal@melix.net> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------
#
  

from Crypto.Cipher import AES
from Crypto import Random
import random
import cStringIO as StringIO
import getpass
from pbkdf2 import pbkdf2
import base64
import hashlib
import time
import os
from cStringIO import StringIO

# for password generation 

alpha = "abcdefghijklmnopqrstuvwxyz"
specials_chars = "#@$_-!?%=()[]"


def generate_password(length=15) :
    random.seed(Random.new().read(6))
    # make sure we have 2 digits 
    dig = str(random.randint(10,100))
    book = alpha + alpha.upper() + specials_chars
    alph = "".join([random.choice(book) for _ in range(length - 2)])
    return alph + dig 


def crypto_pad(txt,bytes_num) :
    r = len(txt)%bytes_num
    b =  bytes_num - r
    pad = b"".join([chr(b)]*b)
    return txt+pad

def crypto_unpad(txt, bytes_num) :
    r = ord(txt[-1])
    return txt[:-r]

class PwDb :
    def __init__(self,path=None,force_create = False):
        self.pwdb = {}
        if path :
            self.path = path
        else :
            if os.path.isfile(".pwmngr") :
                self.path = ".pwmngr"
            else :
                self.path = os.path.expanduser("~/.pwmngr")
        if not os.path.isfile(self.path) :
            if force_create :
                with open(self.path,'w') as f:
                    pass
            else :
                raise IOError


    def parse_file(self) :
        """ read the file and store it pw dict (crptd) """
        with open(self.path) as f :
            for l in f.readlines() :
                try :
                    key, rest = l.split("  ")
                    hsh, value  = rest.split(" ")
                    self.pwdb[key] = {"hash":base64.b64decode(hsh),
                                      "pwd":base64.b64decode(value)}
                except ValueError :
                    continue


    def _update_file(self, key, d) :
        c = StringIO()
        updated = False
        h = base64.b64encode(d["hash"])
        pwd = base64.b64encode(d["pwd"])
        enc_line = "%s  %s %s\n"%(key, h, pwd)
        with open(self.path,'r') as f:
            for l in f :
                key_ , rest = l.split("  ")
                if key_ == key :
                    c.write(enc_line)
                    updated = True
                else :
                    c.write(l)
        if not updated :
            c.write(enc_line)
        with open(self.path,'w') as f :
            f.write(c.getvalue())


    def _get_pwd(self,h) :
        pawd = getpass.getpass("password :")
        return pbkdf2(pawd, h)
        
    def has_key(self,key) :
        return key in self.pwdb

    def set_key(self,key,passwd) :
        crypt, h = self.crypt(passwd)
        data = {"pwd":crypt,"hash":h}
        self._update_file(key,data)

    def get_key(self,key) :
        d = self.pwdb.get(key,None)
        if d :
            return self.decrypt(d["pwd"],d["hash"])
        else :
            raise KeyError


    def crypt(self,pwd) :
        h = hashlib.sha1(str(time.time())).digest()
        dp = self._get_pwd(h)
        ciph = AES.new(dp, AES.MODE_CBC)
        plain = crypto_pad(pwd,16)
        cryptd = ciph.encrypt(plain)
        return cryptd,h

    def decrypt(self,crypt=None, hash=None):
        dp = self._get_pwd(hash)
        ciph = AES.new(dp,AES.MODE_CBC)
        plain = ciph.decrypt(crypt)
        plain = crypto_unpad(plain,16)
        return plain

def main() :

    import argparse

    try :
        import gtk
        cb = gtk.Clipboard()
    except ImportError :
        cb = None 

    parser = argparse.ArgumentParser()
    parser.add_argument("key",nargs=1,help="the key you want to set or retrieve [default action]")
    parser.add_argument("-f","--file",help="the password file (default ~/.pwmngr)")
    parser.add_argument("-g","--generate",action="store_true",help="generate a random password instead of prompting you for the password when setting passwords")
    parser.add_argument("-v","--show", action="store_true",help="default pwmngr store the clear password to clipboard. if set diplay the clear password to stdout")
    parser.add_argument("-s","--set",action="store_true", help="set a password") # get by default ..
    conf = parser.parse_args()

    def output(pwd) :
        if conf.show :
            print pwd
        elif cb :
            cb.set_text(pwd)
            cb.store()
            print "pwd stored to clipboard"
        else :
            print "I cannot talk to a clipboard use --show option explicitely please"
            exit(0)

    def askYorexit(msg) :
            a = raw_input(msg)
            if(a == 'y') :
                return True
            else :
                print "aborting"
                exit(1)

        
    try :
        p = PwDb(conf.file)
    except IOError :
        askYorexit("password file does not exist, do you want to create one ? [N/y]")
        p = PwDb(conf.file, True)

    p.parse_file()
    if(conf.set) :
        if conf.generate :
            pwd = generate_password()
            output(pwd)

        else :
            pwd = getpass.getpass("password to store :")
        if(not p.has_key(conf.key[0])):
            p.set_key(conf.key[0],pwd) 
        else :
            askYorexit("key already exists overwrite ? [N/y]")
            p.set_key(conf.key[0],pwd)
    else :
        pwd = p.get_key(conf.key[0])
        output(pwd)
    

if __name__ == '__main__':
    main()
    
    # p = PassDb("test.pwd")
    # p.add_key("hello","prout")
    # p.save()

    # p2 = PassDb("test.pwd")
    # p2.load()
    # print p.get_key("hello")
    

