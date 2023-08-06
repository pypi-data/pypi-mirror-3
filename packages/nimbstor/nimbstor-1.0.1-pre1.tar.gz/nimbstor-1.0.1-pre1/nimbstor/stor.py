#!/usr/pkg/bin/python2.6

BLOCK_SIZE = 1048576 * 4

import os, sys, hashlib, time, bz2, base64
import cPickle as pickle
import adler64
from itertools import ifilter

compress_function_bz2_method = lambda b: bz2.compress(b, 9)
compress_function_methods = {}
def compress_function(compression, meta):
  if compression: compression = tuple(compression)
  else: compression = (None, 0)
  if meta: return compress_function_bz2_method
  elif compress_function_methods.has_key(compression):
    return compress_function_methods[compression]
  elif compression == ('lzma', 10):
    import lzma
    compress_function_methods[compression] = lambda b: lzma.compress(b, {'level': 9, 'extreme': True})
  elif compression[0] == 'lzma':
    import lzma
    compress_function_methods[compression] = lambda b: lzma.compress(b, {'level': compression[1]})
  elif compression[0] == 'gzip':
    import zlib
    compress_function_methods[compression] = lambda b: zlib.compress(b, compression[1])
  elif compression[0] == 'bzip2':
    compress_function_methods[compression] = lambda b: bz2.compress(b, compression[1])
  elif compression[0] == None:
    compress_function_methods[compression] = lambda b: b
  else: raise SystemError("Unsupported compression type %s" % repr(compression))
  return compress_function_methods[compression]

decompress_function_bz2_method = lambda b: bz2.decompress(b)
decompress_function_methods = {}
def decompress_function(compression, meta):
  if compression: compression = tuple(compression)
  else: compression = (None, 0)
  if meta: return decompress_function_bz2_method
  elif decompress_function_methods.has_key(compression[0]):
    return decompress_function_methods[compression[0]]
  elif compression[0] == 'lzma':
    import lzma
    decompress_function_methods[compression[0]] = lambda b: lzma.decompress(b)
  elif compression[0] == 'gzip':
    import zlib
    decompress_function_methods[compression[0]] = lambda b: zlib.decompress(b)
  elif compression[0] == 'bzip2':
    decompress_function_methods[compression[0]] = lambda b: bz2.decompress(b)
  elif compression[0] == None:
    decompress_function_methods[compression[0]] = lambda b: b
  else: raise SystemError("Unsupported compression type %s" % repr(compression))
  return decompress_function_methods[compression[0]]

aes_keysetup_aes = None
def aes_keysetup(password):
  global aes_keysetup_aes
  if aes_keysetup_aes == None:
    import aes
    aes_keysetup_aes = aes.Keysetup
  return aes_keysetup_aes(password)

def message_encode(buffer, password, meta, compression, bufnum, checksum1, checksum2):
  """Internal function to encode message.

  Args:
    buffer (str): Data buffer.
    password (str): The password as SHA256 hash value.
    meta (boolean): Meta blocks are handled somewhat different.
    compression (tuple): Compression type to use.
    bufnum (int): Current buffer number
    checksum1 (int): Adler64 checksum.
    checksum2 (str): Checksum as returned by stor_stream.checksum(buffer)
  """
  buffer = apply(compress_function(compression, meta), [buffer])
  bufrest = len(buffer) % 16
  if bufrest > 0: buffer = buffer + "\0" * (16 - bufrest)
  if password: buffer = aes_keysetup(password).encrypt(buffer)
  return (buffer, bufnum, checksum1, checksum2)

def message_decode(buffer, password, cksumpwd, meta, compression, bufnum, checksum1, checksum2, bufflen):
  """Internal function to decode message.

  Args:
    buffer (str): Data buffer.
    password (str): The password as SHA256 hash value.
    cksumpwd (str): The password for checksum (MD5 hash value).
    meta (boolean): Meta blocks are handled somewhat different.
    compression (tuple): Compression type to use.
    bufnum (int): Current buffer number
    checksum1 (int): Adler64 checksum.
    checksum2 (str): Checksum as returned by stor_stream.checksum(buffer)
    bufflen (str): Correct data length to return or 0.
  """
  try:
    if password: buffer = aes_keysetup(password).decrypt(buffer)
    buffer = apply(decompress_function(compression, meta), [buffer])
    if bufflen != 0 and len(buffer) > bufflen: buffer = buffer[:bufflen]
    ctx = hashlib.sha256()
    if cksumpwd != None: ctx.update(cksumpwd)
    ctx.update(buffer)
    newcksum = base64.urlsafe_b64encode(ctx.digest())[:-1].upper()
    if newcksum != checksum2: raise SystemError()
  except Exception, err:
    raise SystemError("Wrong password or invalid data (%s)" % repr(err))
  return (buffer, bufnum, checksum1, checksum2, bufflen)


class stor_buffer:
  """Manage buffer for nimbstor.

  Not a performant implementation, should be optimized one day.

  """

  def __init__(self, data = "", splitsize = None):
    """Initialize the buffer.

    Args:
      data (str): Preset buffer content.

    >>> stor_buffer("asdf").value()
    'asdf'
    """
    self._data = [data]
    self._len = len(data)
    self._val = None
    self._splitsize = splitsize

  def __len__(self):
    """Return buffer content length.

    >>> len(stor_buffer("asdfqw"))
    6
    """
    return self._len

  def push(self, data, left = False):
    """Push data to the buffer.

    Args:
      data (str): Data to be pushed.
      left (bool): Push to begin of the buffer (default: False)

    >>> buf = stor_buffer('asdf')
    >>> buf.push('qwer')
    >>> buf.push('zxcv', True)
    >>> buf.value()
    'zxcvasdfqwer'
    """
    self._len += len(data)
    if self._splitsize != None:
      listdat = []
      curpos = 0
      while curpos < self._len:
        listdat.append(data[curpos:curpos + self._splitsize])
        curpos += self._splitsize
      if left: self._data[0:0] = listdat
      else: self._data.extend(listdat)
    else:
      if left: self._data.insert(0, data)
      else: self._data.append(data)
    self._val = None

  def _rmsize(self, size):
    """Internal function to remove some data from buffer.

    Args:
      size (int): Amount of data to remove.

    This function expects, that self._val has correct value.

    >>> buf = stor_buffer('asdfqwer')
    >>> buf.value()
    'asdfqwer'
    >>> buf._rmsize(3)
    >>> buf.value()
    'fqwer'
    """
    new = self._val[size:]
    self._val = None
    self._data = [new]
    self._len = len(new)

  def pop(self, size = None):
    """Pop some data from buffer.

    Args:
      size (int): Amount of data to pop.

    >>> buf = stor_buffer('asdfqwer')
    >>> buf.pop(3)
    'asd'
    >>> buf.value()
    'fqwer'
    """
    if size == None:
      buf = "".join(self._data)
      self._data = []
      self._len = 0
      self._val = None
      return buf
    if len(self._data) == 0:
      return ''
    self._val = None
    buf = []
    restsize = size
    while restsize > 0 and len(self._data) > 0:
      curbuf = self._data[0]
      curlen = len(curbuf)
      if curlen > restsize:
        buf.append(curbuf[:restsize])
        self._data[0] = curbuf[restsize:]
        self._len -= restsize
        restsize = 0
      else:
        buf.append(curbuf)
        del self._data[0]
        self._len -= curlen
        restsize -= curlen
    return ''.join(buf)

  def truncate(self, size = None):
    """Remove some amount of data from buffer.

    Args:
      size (int): Amount of data to remove (default: all).

    >>> buf = stor_buffer('asdfqwer')
    >>> buf.truncate(3)
    >>> buf.value()
    'fqwer'
    """
    if size == None:
      self._data = []
      self._val = None
      self._len = 0
      return
    if self._val == None: self._val = "".join(self._data)
    self._rmsize(size)

  def value(self):
    """Return the buffer value.

    >>> stor_buffer('asdf').value()
    'asdf'
    """
    if self._val == None: self._val = "".join(self._data)
    return self._val

class stor_stream:
  """Base class for storage streams."""

  def __init__(self, password = None, verbose = False):
    """Initialize base stream.

    Args:
      password (str): Optional password to enable encryption.

    >>> stor_stream('asdf')._pass == stor_stream('qwer')._pass
    False
    """
    self._closed = False
    self._pos = 0
    self._known_blocks = {}
    self._known_parts = {}
    self._known_metadata = []
    self._backend = None
    if password != None:
      self._aes = hashlib.sha256(password).digest()
      self._pass = hashlib.md5(password).digest()
    else:
      self._aes = None
      self._pass = None
    self._archive = None
    self._verbose = verbose

  def verbose(self):
    return self._verbose

  def open(self, backend):
    """Initialize and open the stream.

    This function is used in backends to connect the stor_stream with an
    backend.
    """
    self._backend = backend

  def read_buffer(self, number, checksum1, checksum2):
    """Forward read_buffer to the backend."""
    return self._backend.read_buffer(number, checksum1, checksum2)

  def write_buffer(self, buffer, number, checksum1, checksum2):
    """Forward write_buffer to the backend."""
    self._backend.write_buffer(buffer, number, checksum1, checksum2)

  def checksum(self, data):
    """Calculate checksum for given data.
    
    Args:
      data (str): Data buffer.

    Checksum is calculated on data and the password, given in constructor.
    """
    ctx = hashlib.sha256()
    if self._pass != None: ctx.update(self._pass)
    ctx.update(data)
    return base64.urlsafe_b64encode(ctx.digest())[:-1].upper()

  def tell(self):
    """Return the current position in stream."""
    return self._pos

  def archive(self):
    """Tell the archive name.

    The archive name (checksum) is on input streams immediatly available, but
    on output streams is only available after close.
    """
    return self._archive

  def append_block_info(self, number, checksum1, checksum2, backend):
    """Register block info.

    Args:
      number (int): Block number.
      checksum1 (int): Adler64 checksum.
      checksum2 (str): Block checksum as returned by self.checksum(data)
      backend (object): Backend reference, which can read this block.

    Backends use this function to register known blocks.
    """
    checksum1 = int(checksum1, 16)
    if number == 0 and checksum2 not in self._known_metadata:
      self._known_metadata.append(checksum2)
    elif checksum1 == 0: self._known_parts.setdefault(checksum2, []).append(number)
    else: self._known_blocks.setdefault(checksum1, {}).setdefault(checksum2, []).append(number)

  def close(self):
    """Close the stream.

    The backends close will be also called.
    """
    if self._closed: return
    if self._backend != None:
      self._backend.close()

class stor_output(stor_stream):
  """Storage output stream."""

  def __init__(self, password, compression, parent, description, keywords, parlimit = 4, onlyifnew = False, verbose = False):
    """Initialization of output stream.

    Args:
      password (str): Password for encryption (None to disable encryption).
      compression ((str, int)): Compression type as tupple of (method, level).
      parent (str): Name of the parent archive or None.
      description (str): Description of archive.
      keywords (list): List of keyword strings.
      onlyifnew (boolean): Set to True to commit empty (fully deduplicated) archives.
    """
    stor_stream.__init__(self, password, verbose)
    self._metadata = {
	'description': description,
	'keywords': keywords,
	'metainfo': [],
	'timestamp': time.time(),
	'parent': parent,
	'compression': compression,
	'blocks': [],
	'size': 0,
    }
    self._procslimit = parlimit
    if parlimit != None:
      import multiprocessing
      self._procspool = multiprocessing.Pool(parlimit)
      self._procslist = []
    self._buffer = stor_buffer()
    self._bufnum = 1
    self._bufsize = BLOCK_SIZE * 2
    self._checksum2 = None
    self._size = 0
    self._something_written = False
    self._onlyifnew = onlyifnew
    self._compression = compression

  def write(self, buffer):
    """Write function.

    Use this function to write data to the stream.
    """
    buflen = len(buffer)
    self._pos += buflen
    self._buffer.push(buffer)
    self.flush_buffer(self._bufsize)

  def size(self):
    """Returns the size (length) of stream."""
    return self._metadata['usage']

  def set_metainfo(self, info):
    """Set the meta information, user defined."""
    self._metadata['metainfo'] = info

  def set_parent(self, parent):
    """Set the parent archive name."""
    self._metadata['parent'] = parent

  def _block_already_exists(self, buffer, begin, end, checksum1):
    """Checks if the given block already exists.

    Args:
      buffer (str): Data buffer.
      begin (int): Block start position.
      end (int): Block end position.

    Call only if the block with given Adler64 checksum really exist (it means
    that it was registred with append_block_info).
    """
    checksum2 = self.checksum(buffer[begin:end])
    if self._known_blocks[checksum1].has_key(checksum2):
      self._checksum2 = checksum2
      self._checksumblock = self._known_blocks[checksum1][checksum2]
      if self._verbose:
        print "@ deduplication:", checksum2
      return True
    return False

  def close(self):
    """Close the output stream.

    This function write also the metadata, without metadata the archive does
    not exist.
    """
    if self._closed: return
    try:
      try:
        if self._backend != None:
          self.flush_buffer(BLOCK_SIZE)
          self.commit_buffer(self._buffer.pop(), 0)
          if not self._onlyifnew or self._something_written:
            self._finish_write(0)
            self._metadata['usage'] = self._size
            self._metadata['size'] = self._pos
            buffer = pickle.dumps(self._metadata)
            self._bufnum = 0
            self.commit_buffer(buffer, 0, meta = True)
            self._finish_write(0)
      finally: stor_stream.close(self)
    finally:
      self._procspool.terminate()
      self._procspool.join()

  def flush_buffer(self, tosize):
    """Flush data from buffer.
    
    This function do the deduplication with Adler64.
    """
    while len(self._buffer) >= tosize:
      buffer = self._buffer.value()
      found, pos, dest, fcks, cks = adler64.search(self._known_blocks, self._block_already_exists, buffer, BLOCK_SIZE)
      if found:
	destlen = len(dest)
	if destlen == BLOCK_SIZE: pass
	elif destlen > 0: self.commit_buffer(dest, 0)
	checksum1 = "%016X" % cks
	self._metadata['blocks'].append((self._checksumblock, checksum1, self._checksum2, BLOCK_SIZE))
	self._bufnum += 1
	self._checksum2 = None
	self._buffer.truncate(pos + BLOCK_SIZE + destlen)
      else:
	self.commit_buffer(self._buffer.pop(BLOCK_SIZE), fcks)

  def _finish_write(self, limit):
    while len(self._procslist) > limit:
      proc = self._procslist.pop(0)
      buffer, bufnum, checksum1, checksum2 = proc.get()
      self._size += len(buffer)
      self._backend.write_buffer(buffer, bufnum, checksum1, checksum2)

  def commit_buffer(self, buffer, checksum1int, meta = False):
    """Write data to the beckend.

    Args:
      buffer (str): Block buffer.
      checksum1int (int): Adler64 checksum of the buffer.
      meta (boolean): Set to True if the buffer contains metadata.
    """
    checksum1 = "%016X" % checksum1int
    checksum2 = self.checksum(buffer)
    buflen = len(buffer)
    if checksum1int == 0 and self._known_parts.has_key(checksum2):
      self._metadata['blocks'].append((self._known_parts[checksum2], checksum1, checksum2, buflen))
    else:
      self._something_written = True
      msgencode_args = [
          buffer,
          self._aes,
          meta,
          self._compression,
          self._bufnum,
          checksum1,
          checksum2,
      ]
      if self._procslimit != None:
        self._procslist.append(self._procspool.apply_async(message_encode, msgencode_args))
        self._finish_write(self._procslimit)
      else:
        buffer, bufnum, checksum1, checksum2 = apply(message_encode, msgencode_args)
        self._size += len(buffer)
        self._backend.write_buffer(buffer, bufnum, checksum1, checksum2)
      self._metadata['blocks'].append((self._bufnum, checksum1, checksum2, buflen))
    if not meta: self._bufnum += 1
    else: self._archive = checksum2

class stor_input(stor_stream):
  """Storage input stream."""

  def __init__(self, password, archive, parlimit = 4, verbose = False):
    """Initialization of input stream.

    Args:
      password (str): Password for decrypting data (or None).
      archive (str): Name of the archive (checksum).
    """
    stor_stream.__init__(self, password, verbose)
    self._procslimit = parlimit
    if parlimit != None:
      import multiprocessing
      self._procspool = multiprocessing.Pool()
      self._procslist = []
    self._archive_checksum = archive
    self._buffer = stor_buffer(splitsize = 10240)
    self._archive = archive
    self._prof = 0

  def open(self, backend):
    """Initialize backend for reading.

    To read data, we need to read the metadata first. This function should be
    called by backend, if the backend is ready.
    """
    stor_stream.open(self, backend)
    if self._archive_checksum not in self._known_metadata:
      raise SystemError("Archive %s not found." % repr(self._archive_checksum))
    ck1 = "%016X" % 0
    ck2 = self._archive_checksum
    bufgen = self.read_buffer(0, ck1, ck2)
    self._metadata = None
    for buffer in bufgen:
      try:
        buffer, _, _, _, _ = message_decode(buffer, self._aes, self._pass, True, None, 0, ck1, ck2, 0)
        self._metadata = pickle.loads(buffer)
      except Exception, err: continue
      break
    if self._metadata == None:
      raise SystemError('Failed to read metdata')
    self._compression = self._metadata['compression']
    self._blocks = self._metadata['blocks'][:]

  def bocks(self):
    return [(0, "%016X" % 0, self._archive_checksum),] + sef._metadata['blocks']

  def close(self):
    if self._closed: return
    try: stor_stream.close(self)
    finally:
      self._procspool.terminate()
      self._procspool.join()

  def read(self, size):
    """Read data of given size.

    Use this function to read the data.
    """
    data = None
    if self._procslimit != None:
      while len(self._buffer) < size and (len(self._blocks) > 0 or len(self._procslist) > 0):
        data = None
        while len(self._procslist) < self._procslimit and len(self._blocks) > 0:
          num, ck1, ck2, blen = self._blocks.pop(0)
          buffer_generator = self.read_buffer(num, ck1, ck2)
          self._procslist.append((
            buffer_generator,
            self._procspool.apply_async(message_decode, [
              buffer_generator.next(),
              self._aes, self._pass, False, self._compression,
              num, ck1, ck2, blen,
            ]),
            num, ck1, ck2, blen))
        if self._procslimit != None:
          bufgen, proc, num, ck1, ck2, blen = self._procslist.pop(0)
          try: data, num, ck1, ck2, blen = proc.get()
          except Exception, err: data = None
          while data == None:
            data = bufgen.next()
            try:
              data, num, ck1, ck2, blen = apply(message_decode, [
                data, self._aes, self._pass, False, self._compression,
                num, ck1, ck2, blen,
              ])
            except Exception, err: data = None
        self._buffer.push(data)
    else:
      while len(self._buffer) < size and len(self._blocks) > 0:
        data = None
        num, ck1, ck2, blen = self._blocks.pop(0)
        for buffer in self.read_buffer(num, ck1, ck2):
          try:
            data, num, ck1, ck2, blen = apply(message_decode, [
              data, self._aes, self._pass, False, self._compression,
              num, ck1, ck2, blen,
            ])
          except Exception, err: continue
          break
        self._buffer.push(data)
    x = time.time()
    data = self._buffer.pop(size)
    self._prof += time.time() - x
    return data

  def metainfo(self):
    """Returns user defined metadata."""
    return self._metadata['metainfo']

class stor_util(stor_stream):
  """Storage stream utility.

  This storage type is used to manage the archives, f.e. to search, copy,
  remove, ...
  """

  def __init__(self, password):
    stor_stream.__init__(self, password)
    self._errors = []
    self._metadata_data = {}

  def open(self, backend):
    stor_stream.open(self, backend)
    checksum1 = "%016X" % 0
    for metadata in self._known_metadata:
      bufgen = self.read_buffer(0, checksum1, metadata)
      data = None
      try:
        for buffer in bufgen:
          try:
            data, _, _, _, _ = message_decode(buffer, self._aes, self._pass, True, None, 0, checksum1, metadata, 0)
            data = pickle.loads(data)
          except Exception, err: continue
          break
      except Exception, err:
        self._errors.append((metadata, err))
        continue
      if data != None:
        self._metadata_data[metadata] = data

  def search(self, keywords):
    """Search for an archive.

    Args:
      keywords (list): List of strings, for which should be searched.

    The search function search for an archive, gives each archive weight (how
    good it matches with given keywords), sort it in ascend order and return
    the list of archvies, the dependecies between archives and list of errors
    on search.
    """
    result = []; parents = {}
    for metadata, data in self._metadata_data.items():
      if len(keywords) > 0:
        weight = 0
        for kwd in keywords:
          for fnd in ifilter(lambda x: x == kwd, data['keywords']): weight += 10
          for fnd in ifilter(lambda x: kwd in x and x != kwd, data['keywords']): weight += 3
          if kwd in time.strftime("%F %R", time.localtime(data['timestamp'])): weight += 2
          if kwd in str(data['size']): weight += 1
          if kwd.lower() in data['description'].lower(): weight += 5
          if kwd in repr(data['metainfo']): weight += 1
        result.append({
          'weight':       weight,
          'id':           metadata,
          'description':  data['description'],
          'keywords':     data['keywords'],
          'size':         data['size'],
          'usage':        data['usage'],
          'timestamp':    data['timestamp'],
          'parent':       data['parent'],
        })
      else:
        result.append({
          'weight':       0,
          'id':           metadata,
          'description':  data['description'],
          'keywords':     data['keywords'],
          'size':         data['size'],
          'usage':        data['usage'],
          'timestamp':    data['timestamp'],
          'parent':       data['parent'],
        })
      parents.setdefault(data['parent'], []).append(metadata)
    if len(keywords) > 0: result.sort(key = lambda x: x['weight'])
    else: result.sort(key = lambda x: x['description'])
    return (result, parents, self._errors)

  def keywords(self):
    """Return list of used keywords."""
    keywords = {}
    for metadata, data in self._metadata_data.items():
      for kwd in data['keywords']:
	keywords[kwd] = keywords.get(kwd, 0) + 1
    return (keywords, self._errors)

  def block_exists(self, number, checksum1, checksum2):
    if type(checksum1) != type(0):
      checksum1 = int(checksum1, 16)
    if number == 0:
      if checksum2 in self._known_metadata:
        return True
    elif checksum1 == 0:
      if self._known_parts.has_key(checksum2):
        if number in self._known_parts[checksum2]:
          return True
    else:
      if self._known_blocks.has_key(checksum1):
        if self._known_blocks[checksum1].has_key(checksum2):
          if number in self._known_blocks[checksum1][checksum2]:
            return True
    return False

  def blocks(self, archive):
    ck1 = "%016X" % 0
    metadata = None
    return [(0, ck1, archive, 0)] + self._metadata_data[archive]['blocks'][:]

__all__ = ('stor_output', 'stor_input', 'stor_util')
# vim:sts=2:sw=2:
