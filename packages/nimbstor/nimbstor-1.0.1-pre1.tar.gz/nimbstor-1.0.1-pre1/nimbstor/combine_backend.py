#!/usr/pkg/bin/python2.6 -O

import random

class combine_backend:
  def __init__(self, nimbstor, redundancy = 1, verbose = False):
    self._nimbstor = nimbstor
    self._backends = []
    self._block_directory = {}
    self._redundancy = redundancy
    self._verbose = verbose

  def open(self, backend):
    self._backends.append(backend)

  def activate(self):
    self._nimbstor.open(self)

  def close(self):
    for backend in self._backends:
      backend.close()

  def append_block_info(self, number, checksum1, checksum2, backend):
    self._block_directory.setdefault((number, checksum1, checksum2), []).append(backend)
    self._nimbstor.append_block_info(number, checksum1, checksum2, self)

  def write_buffer(self, buffer, number, checksum1, checksum2):
    written_count = 0
    write_backends = self._backends[:]
    random.shuffle(write_backends)
    if number == 0: redundancy = len(write_backends)
    else: redundancy = self._redundancy
    while written_count < redundancy:
      if len(write_backends) == 0 and written_count == 0:
	raise SystemError("Could not write to destination backends")
      elif len(write_backends) == 0 and written_count > 0:
	sys.stderr.write("Could only write %d blocks for %s\n" % (written_count, repr((number, checksum1, checksum2))))
	break
      backend = write_backends.pop()
      backend.write_buffer(buffer, number, checksum1, checksum2)
      written_count += 1

  def read_buffer(self, number, checksum1, checksum2):
    read_backends = self._block_directory[(number, checksum1, checksum2)]
    random.shuffle(read_backends)
    for backend in read_backends:
      try: data = backend.read_buffer(number, checksum1, checksum2).next()
      except Exception, err: continue
      yield data
    raise SystemError("Failed to read block: " + repr((number, checksum1, checksum2)))

__all__ = ('combine_backend',)
