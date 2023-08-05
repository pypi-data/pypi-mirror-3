PwMngr 
======

A CLI password manager. 

pwmngr was designed with a few requirement : 
* use a dead simple CLI interface
* have a readable text file as backend, that could be checked in a vcs, or 
  carried around the cloud. 
* be secure. 


security disclaimer
===================

Disclaimer : this software was not written by a cryptography specialist, and needs to be checked-out by specialists. 

However, this tool make use of proven algorithms : Passwords are encrypted using AES256, (courtesy of PyCrypto), with the encryption key being generated from your password, a random hash (different for each of your passwords) and the pbkdf2 key derivation algorithm. 

The rationale is that you can encrypt all your password with the same master password, a different encryption key is generated for your passwords.


usage
=====
example
-------

  $ ./pwmngr -s test.site.net
  password file does not exist, do you want to create one ? [N/y]y
  password to store : <mypassword>
  password :<secret>
  $ ./pwmngr -g test.site.net
  password :<secret>
  pwd stored to clipboard
  $ ./pwmngr -vg test.site.net
  password :<secret>
  mypassword


default password file is located at ~/.pwmngr 
it's up to you to symlink or indicate alternative file with -f option.

manual
------
usage: pwmngr [-h] [-f FILE] [-g] [-v] [-s] key

positional arguments:
  key                   the key you want to set or retrieve [default action]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  the password file (default ~/.pwmngr)
  -g, --generate        generate a random password instead of prompting you
                        for the password when setting passwords
  -v, --show            default pwmngr store the clear password to clipboard.
                        if set diplay the clear password to stdout
  -s, --set             set a password
