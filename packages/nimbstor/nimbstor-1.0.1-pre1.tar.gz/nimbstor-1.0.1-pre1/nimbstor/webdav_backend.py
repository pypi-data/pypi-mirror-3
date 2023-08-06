#!/usr/pkg/bin/python2.6 -O

import os, tinydav, re

class webdav_backend:
  def __init__(self, nimbstor, proto, host, port, basedir, user, password, verbose = False):
    if basedir.endswith('/'): self._basedir = basedir
    else: self._basedir = basedir + '/'
    self._nimbstor = nimbstor
    self._verbose = verbose
    self._connection = tinydav.WebDAVClient(host, int(port), proto)
    self._connection.setbasicauth(user, password)
    re_fname = re.compile(r'.*/([0-9]{7})\.([0-9]+)\.([0-9A-Za-z_-]+)$')
    for fname in self._connection.propfind(self._basedir, depth = 1):
      ma_fname = re_fname.match(fname.href)
      if not ma_fname: continue
      number = int(ma_fname.group(1))
      checksum1 = ma_fname.group(2)
      checksum2 = ma_fname.group(3).upper()
      #if self._verbose: print "WebDAV FOUND:", fname.href
      self._nimbstor.append_block_info(number, checksum1, checksum2, self)

  def activate(self):
    self._nimbstor.open(self)

  def write_buffer(self, buffer, number, checksum1, checksum2):
    fname = os.path.join(self._basedir, "%07d.%s.%s" % (number, checksum1, checksum2))
    #if self._verbose: print "WebDAV PUT:", fname
    self._connection.put(fname, buffer)
    self._nimbstor.append_block_info(number, checksum1, checksum2, self)

  def read_buffer(self, number, checksum1, checksum2):
    fname = os.path.join(self._basedir, "%07d.%s.%s" % (number, checksum1, checksum2))
    #if self._verbose: print "WebDAV GET:", fname
    ret = self._connection.get(fname)
    yield ret.content

  def close(self):
    pass

__all__ = ('directory_backend',)
# vim:sts=2:sw=2:
