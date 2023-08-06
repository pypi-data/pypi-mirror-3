cdef unsigned long _character_table[256]
def _initialize():
    cdef unsigned int i = 0
    for n in [
0x272ab691, 0xcde74fe9, 0xf530e162, 0x96f9db97, 0x6150d109, 0x2e6ee7e3,
0xb191c9bb, 0xf898f264, 0x84daacc3, 0x16fcc550, 0x73ca0ba5, 0x4f30b942,
0xf459c982, 0xa2c7cf3e, 0x69d0eebf, 0xf945e6f0, 0x8d8c92e8, 0xf92a953b,
0x225300d0, 0xb1f45ef3, 0xa97278fc, 0x4ed65be1, 0xb91f3643, 0x3cf6860f,
0xa49a98ad, 0x10ab3945, 0x8ae79aa4, 0xd792a6d1, 0x266ef44b, 0x41c74186,
0x11379127, 0x3f206606, 0xb47e3c07, 0xf69ec345, 0x01c1a523, 0xc2184745,
0xfd06267e, 0x7f2f9425, 0x4e66ea90, 0xbcdf4162, 0xaa405927, 0x42a16d54,
0x2d99ee8b, 0x17c062f8, 0x7e33e0e4, 0x86e557fa, 0xe4ff37da, 0xd7c686e9,
0xed0d3a7b, 0x5f2629ca, 0xaa6d5760, 0x986818d5, 0x6a3eeb12, 0xc41c117b,
0x91ae88a9, 0xd036e9a5, 0x22eca8b6, 0x69953343, 0x27a5e263, 0x17061403,
0xee6312d7, 0x3cc55561, 0x0dba16de, 0x4037f0df, 0xd39dfac9, 0x972e9c95,
0xa2a7c492, 0x00261bec, 0xa11f3c43, 0x1a3558a6, 0x881d5699, 0xffd58820,
0xba9825e3, 0xd7b0e0da, 0x9ec27531, 0xb668a438, 0x6e2771a9, 0xe40b8083,
0xe48d063b, 0x1c018f32, 0xd92dcd79, 0xaec3736d, 0x7b85bdbf, 0x4e065cd0,
0xa2faf39a, 0x865ef270, 0x015e3e66, 0x88f96a1c, 0x99d55337, 0x7d254fe5,
0x4a7ac9fe, 0x7057c1df, 0x8d1e48e4, 0x7c2f2428, 0x855181fa, 0x792f9127,
0x9594e712, 0xb29f8a1a, 0xc54137f0, 0x7060abca, 0x5af94e9b, 0xb7186ba2,
0xf641ce19, 0x81b920e0, 0xcc92973a, 0xa1bbde27, 0x451027d4, 0xd95fdf40,
0x30594811, 0x1d4c8f17, 0x19b7aa23, 0xf53f6a0b, 0x62c86021, 0xee3f4064,
0xdc9b4c2c, 0x00629d23, 0x9f96eed2, 0xb6cf5501, 0xe06037b8, 0x1e7581b3,
0x31dc3c74, 0xcf686d6b, 0xf55bf9b9, 0x61dc32a2, 0xf86082b5, 0xe2f7141a,
0x5d6842bd, 0x4311d121, 0xc11c3527, 0x9ef27a12, 0x113e377b, 0xd4418923,
0x1d27d9c7, 0x2f314359, 0x8abb514e, 0x984ba5dd, 0x749e716c, 0x6ddb6377,
0x91b1ceb5, 0xd8a8b64e, 0xd034705a, 0xa80b09f9, 0xdb26b3cf, 0x91dcc1b3,
0x048546b2, 0x97ee9eee, 0xa51f5ae7, 0x926c8c10, 0xa95978ff, 0xbd7dcf6f,
0xdb6094e2, 0x3486eaa9, 0x8d6748ab, 0x8f13aa15, 0xbbc159d0, 0x2ed4288e,
0x254fec86, 0x137fcb7a, 0x62f30964, 0x551d7b09, 0xcadb5947, 0x57609ac0,
0x24e13b75, 0xc5be8632, 0x7fb49a03, 0xd7d8960d, 0x160b207b, 0xed12f15e,
0x4d28b8b9, 0x6cf0af0c, 0xb5787215, 0xfc520ba7, 0x48aa36c6, 0x7639b765,
0x392bf384, 0xed8a806c, 0xbb1b156f, 0x0c7edd4f, 0x9935822f, 0xf2b01bd4,
0xe71f6e5d, 0xc39b37fa, 0x17c5b621, 0x39ed9f40, 0x70fa9c1b, 0x17c46422,
0xaee51288, 0x45aca5e2, 0x78b8f29c, 0xf9dc3084, 0x7eb0c634, 0xb3059924,
0x0da807b0, 0x0e9b5a62, 0x113efc1d, 0x2d89b53b, 0xc05f8b92, 0x1ca759ff,
0x0b8cbbde, 0x7b991d9d, 0xbedcb15e, 0xd5e53f23, 0xad175a32, 0x02b70186,
0x14722792, 0xa09b9da0, 0x5203797d, 0xdf8dd077, 0x5d8ea095, 0x453589c3,
0x05f39a47, 0xb1957eaf, 0x7d9beb2d, 0x6db8a4e2, 0x17f03bb7, 0x868dd9b8,
0xab789b07, 0xb44039d6, 0x8a038c1c, 0xe63eecdd, 0x774e4132, 0x960f697c,
0x296aa969, 0xdb3175ac, 0x42c634a4, 0x010c6738, 0x167e71b4, 0xf951687b,
0x02deeab4, 0x59b6c56c, 0x85b5e3b6, 0xcfac84dc, 0x08e3df9f, 0xc7ead201,
0x8d640f4d, 0xe6befa2f, 0xfe4a0f03, 0x510402e6, 0xe61395fe, 0x69001c10,
0x3572fc65, 0xc6307289, 0x9da1bb6d, 0xd7a126e4, 0xef984bb0, 0xd6076c64,
0xdf7b05e2, 0xb9b01451, 0x3e61e9ad, 0xa0b5096c, 0x1e9b6ed0, 0x08107fc1,
0xb5e8c48c, 0x064cdca1, 0x20342345, 0x34fc9ae7 ]:
        _character_table[i] = n
        i = i + 1
_initialize()

def rolling_checksum(buf):
    cdef unsigned long cksum = 0
    cdef unsigned long i = 0
    cdef unsigned long buflen = len(buf)
    cdef unsigned char* chrbuf = buf

    while i < buflen:
        cksum = cksum ^ _character_table[chrbuf[i]]
        i = i + 1

    return cksum

def rolling_search(dic, checkfunc, buf, blocksize):
    cdef unsigned long cksum = 0
    cdef unsigned long fcks = 0
    cdef unsigned long i = 0 
    cdef unsigned long pos = 0 
    cdef unsigned long end = 0 
    cdef unsigned long buflen = len(buf)
    cdef unsigned long bs = blocksize
    cdef unsigned char* chrbuf = buf

    while i < bs:
        cksum = cksum ^ _character_table[chrbuf[i]]
        i = i + 1

    fcks = cksum ; end = buflen - bs - 1
    while pos < end:
        if dic.has_key(cksum):
            if checkfunc(chrbuf[pos:pos+bs], pos, cksum):
                return (pos, cksum)
        cksum = cksum ^ _character_table[chrbuf[pos]]
        cksum = cksum ^ _character_table[chrbuf[pos+bs]]
        pos = pos + 1
    return (None, fcks)

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
   
# vim:sts=4:sw=4:
