#!/usr/pkg/bin/python2.6 -O

import os, re, getpass
from paramiko import SFTPClient, Transport, RSAKey, DSSKey, SSHException

class sftp_backend:
    def __init__(self, nimbstor, host, port, basedir, user, password, verbose = False):
        self._nimbstor = nimbstor
        self._basedir = basedir
        self._verbose = verbose
        if password == '':
            password = getpass.unix_getpass(prompt = '      sFTP password: ')
        elif os.path.exists(os.path.expanduser(password)):
            try: password = RSAKey.from_private_key_file(os.path.expanduser(password))
            except SSHException:
                try: password = DSSKey.from_private_key_file(os.path.expanduser(password))
                except SSHException: pass
        self._transport = Transport((str(host), int(port)))
        if type(password) == str:
            self._transport.connect(username = user, password = password)
        else: self._transport.connect(username = user, pkey = password)
        self._connection = SFTPClient.from_transport(self._transport)
        self._connection.chdir(self._basedir)
        re_fname = re.compile(r'^([0-9]{7})\.([0-9A-Fa-f]+)\.([0-9A-Za-z_-]+)$')
        for fname in self._connection.listdir():
            ma_fname = re_fname.match(fname)
            if not ma_fname: continue
            number = int(ma_fname.group(1))
            checksum1 = ma_fname.group(2)
            checksum2 = ma_fname.group(3).upper()
            #if self._verbose: print "SFTP FOUND:", fname
            self._nimbstor.append_block_info(number, checksum1, checksum2, self)
  
    def activate(self):
        self._nimbstor.open(self)
  
    def write_buffer(self, buf, number, checksum1, checksum2):
        fname = "%07d.%s.%s" % (number, checksum1, checksum2)
        #if self._verbose: print "SFTP PUT:", fname
        fd = self._connection.open(fname, 'w')
        try: fd.write(buf)
        finally: fd.close()
        self._nimbstor.append_block_info(number, checksum1, checksum2, self)
  
    def read_buffer(self, number, checksum1, checksum2):
        fname = "%07d.%s.%s" % (number, checksum1, checksum2)
        #if self._verbose: print "SFTP GET:", fname
        fd = self._connection.open(fname, 'r')
        try: buf = fd.read()
        finally: fd.close()
        return buf
  
    def close(self, dont_commit = False):
        self._connection.close()

# vim:sts=4:sw=4:
