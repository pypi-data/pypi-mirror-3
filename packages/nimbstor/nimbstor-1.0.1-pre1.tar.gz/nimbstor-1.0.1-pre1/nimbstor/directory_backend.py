#!/usr/pkg/bin/python2.6 -O

import os, sys, random, hashlib

def read_directory_content(directory):
  content = []
  for fname in os.listdir(directory):
    number, checksum1, checksum2 = fname.split('.')
    number = int(number)
    content.append((number, checksum1, checksum2))
  return content

class directory_backend:
  def __init__(self, nimbstor, directory, verbose):
    self._directory = directory
    self._nimbstor = nimbstor
    self._verbose = verbose
    for number, checksum1, checksum2 in read_directory_content(directory):
      self._nimbstor.append_block_info(number, checksum1, checksum2, self)

  def activate(self):
    self._nimbstor.open(self)

  def write_buffer(self, buffer, number, checksum1, checksum2):
    fname = os.path.join(self._directory, "%07d.%s.%s" % (number, checksum1, checksum2))
    if os.path.exists(fname):
      raise SystemError("DB: INTERNAL ERROR - block %s already exists" % fname)
    fd = open(fname, 'w')
    fd.write(buffer)
    fd.close()
    # if self._verbose: print "DB: written", fname
    self._nimbstor.append_block_info(number, checksum1, checksum2, self)

  def read_buffer(self, number, checksum1, checksum2):
    fname = os.path.join(self._directory, "%07d.%s.%s" % (number, checksum1, checksum2))
    if not os.path.exists(fname):
      raise SystemError("DB: INTERNAL ERROR - block %s not exists" % fname)
    fd = open(fname, 'r')
    buffer = fd.read()
    fd.close()
    # if self._verbose: print "DB: readen", fname
    yield buffer

  def close(self):
    pass

__all__ = ('directory_backend',)
# vim:sts=2:sw=2:
