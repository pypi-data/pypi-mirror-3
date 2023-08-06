#!/usr/pkg/bin/python2.6 -O

""" Prepare data for tests.


  >>> os.system('rm -rf out1 out2 out3 .nimbstor_parent || true')
  0
  >>> os.mkdir('out1')
  >>> os.mkdir('out2')
  >>> os.mkdir('out3')
  >>> seq1 = "".join([chr(random.randint(40, 60)) for x in xrange(1024 + 7777)] * 127)
  >>> seq2 = "".join([chr(random.randint(40, 60)) for x in xrange(1024 + 7777)] * 127)
  >>> seq3 = "".join([chr(random.randint(40, 60)) for x in xrange(1024 + 7777)] * 127)
  >>> open('f1', 'w+').write(seq1)
  >>> open('f2', 'w+').write(seq2)
  >>> open('f3', 'w+').write(seq3)
  >>> opt = command_tar_arguments(['test', '-v', '-p', 'qwer', '-m', '10', '-d', 'out1', 'out2', 'out3', '-D', 'test1', '-K', 'kwd1', '-c', 'f1', 'f2', 'f3'])
  >>> command_create_archive(opt, time.time())
  Use following backends: out1, out2, out3
  f1
  f2
  f3
  Archive ...

"""

import os, sys, time, random, getpass, re
from tarfile import TarFile, PAX_FORMAT, open as taropen, filemode, CHRTYPE, BLKTYPE, SYMTYPE, LNKTYPE, DIRTYPE
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from nimbstor import stor_input, stor_output, stor_util

class NimbTarFile(TarFile):
  def __init__(self, verbose, *options, **keywords):
    TarFile.__init__(self, *options, **keywords)
    self._recorded_files_list = []
    self._verbose = verbose

  def addfile(self, tarinfo, fileobj = None):
    self._recorded_files_list.append(tarinfo.get_info('UTF-8', 'replace'))
    tarinfo.name = re.sub(r'^[./]*', '', os.path.normpath(tarinfo.name))
    if self._verbose:
      print tarinfo.name
    return TarFile.addfile(self, tarinfo, fileobj)

  def recorded_files(self):
    return self._recorded_files_list

def create_archive(output, files, verbose = False):
  tar = NimbTarFile(
      verbose = verbose,
      fileobj = output,
      mode = 'w',
      encoding = PAX_FORMAT)
  try:
    for filename in files:
      tar.add(filename, recursive = True)
  finally: tar.close()
  output.set_metainfo(tar.recorded_files())

def extract_archive(input, files = [], verbose = False):
  try:
    tar = taropen(fileobj = input, mode = 'r|')
    try:
      member = tar.next()
      while member:
        if len(files) > 0:
          if member.name in files:
            tar.extract(member)
            if verbose:
              print member.name
              sys.stdout.flush()
        else:
          tar.extract(member)
          if verbose:
            print member.name
            sys.stdout.flush()
        member = tar.next()
    finally: tar.close()
  finally: input.close()

def list_archive(input, files = [], verbose = False):
  for finfo in input.metainfo():
    if len(files) > 0 and finfo['name'] not in files: continue
    if verbose:
      print filemode(finfo['mode']),
      print "%s/%s" % (finfo['uname'] or finfo['uid'], finfo['gname'] or finfo['gid']),
      if finfo['type'] == CHRTYPE or finfo['type'] == BLKTYPE:
        print "%10s" % ("%d,%d" % (finfo['devmajor'], finfo['devminor'])),
      else: print "%10d" % finfo['size'],
      print "%d-%02d-%02d %02d:%02d:%02d" % time.localtime(finfo['mtime'])[:6],
    print finfo['name'],
    if verbose:
      if finfo['type'] == SYMTYPE: print "->", finfo['linkname'],
      if finfo['type'] == LNKTYPE: print "link to", finfo['linkname'],
    print
  input.close()

def search_archive(util, keywords, verbose = False):
  result, parents, errors = util.search(keywords)
  print "% 6s" % "WEIGHT",
  print "%- 43s" % "ARCHIVE",
  print " %- 17s" % "CREATED",
  print " %- 13s" % "SIZE",
  print " %- 13s" % "USAGE",
  print "DESCRIPTION"
  for res in result:
    if not verbose and parents.has_key(res['id']): continue
    print "% 6d" % res['weight'],
    print res['id'],
    print " " + time.strftime("%F %R", time.localtime(res['timestamp'])),
    print " %- 13d" % res['size'],
    print " %- 13d" % res['usage'],
    print " " + res['description']
  if verbose:
    for metadata, error in errors:
      print "WARNING:", str(error)

def list_keywords(util, verbose = False):
  keywords, errors = util.keywords()
  keywords = keywords.items()
  keywords.sort(key = lambda x: x[0])
  print "%- 30s %- 5s" % ("KEYWORD", "USAGE")
  for kwd, usage in keywords:
    print "%- 30s%- 5d" % (kwd, usage)
  if verbose:
    for metadata, error in errors:
      print "WARNING:", str(error)

def copy_archive(source_stor, dest_stor, archive, verbose = False):
  block_list = source_stor.blocks(archive)
  if verbose:
    sys.stdout.write("Copy %d blocks " % len(block_list))
    sys.stdout.flush()
  for number, checksum1, checksum2, length in block_list:
    if not dest_stor.block_exists(number, checksum1, checksum2):
      buffer = source_stor.read_buffer(number, checksum1, checksum2).next()
      dest_stor.write_buffer(buffer, number, checksum1, checksum2)
      if verbose: sys.stdout.write('.'); sys.stdout.flush()
    else:
      if verbose: sys.stdout.write('+'); sys.stdout.flush()
  if verbose:
    sys.stdout.write(' done.\n')

def command_tar_arguments(args, config_files = []):
  optparser = ArgumentParser(
      fromfile_prefix_chars = '@',
      formatter_class = RawDescriptionHelpFormatter,
      description = """Store deduplicated, compressed and encrypted data failsafe distributed over
filesystems, sFTP accounts, IMAP mailboxes or WebDAV shares.
""",
      epilog = """

The nimbstor allows you to store archives in different places through
simple backends. It comes with tool nimbtar, which stores tar archives,
but with following additional features:

  * Store multiple archives with description and keywords
  * Search for description, keywords and filenames
  * List archive contents without reading it
  * Distribute the tar archive over several storage places
  * Use deduplication to store multiple copies of same data efficiently
  * Create redundancy to compensate fail of one or more storage places
  * Encrypt data with AES 256

Following backends are supported for now: filesystems, IMAP, WebDAV,
SFTP. To use it, you need to set the STORAGE parameter to following
valeus:

  Filesystem    <directory name>

  IMAP          imap:<host>:<port>:<user>:<password>:<mailbox>
                imaps:<host>:<port>:<user>:<password>:<mailbox>

  WebDAV        webdav:<host>:<port>:<user>:<password>:<directory>
                webdavs:<host>:<port>:<user>:<password>:<directory>

  SFTP          sftp:<host>:<port>:<user>:<password>:<directory>
                (You can use path to you private key as password)

If you specify multiple backends, then the archives will be distributed
over all backends and also the specified redundancy will be ccreated.
You can also specify PARALLEL parameter to parallalize the archivation
process.

Per default it will read the ~/.nimbtarrc and /etc/nimbtarrc config
files, if they are exists. This files can contain command line arguments
which you would preset. If environment variable NIMBTARCFG is set, then
the file specified there will be used instead.

ADDITIONAL REQUIREMENTS:

  Encryption              alo_aes
  LZMA compression        pyliblzma
  Parallelization         multiprocessing
                          (only for python 2.6 and less)
  WebDAV                  tinydav
  sFTP                    paramiko

You can install the requirements simply with pip or easy_install.

""")

  optparser.add_argument('-e', '--empty', action = 'store_true', help = 'Empty archive schould be written also.')
  optparser.add_argument('-v', '--verbose', action = 'store_true', help = 'Verbose mode.')

  optparser.add_argument('-d', '--storage', required = True, nargs = '+', help = 'Use given storages as archive.')
  optparser.add_argument('-D', '--desc', help = 'Description of the archive.')
  optparser.add_argument('-K', '--keywords', nargs = '+', metavar = 'KWD', help = 'List of keywords for archive.')

  optparser.add_argument('-a', '--archive', metavar = 'ID', help = 'Give the archive ID to use (as parent for creation).')
  optparser.add_argument('-r', '--redundancy', type = int, default = 1, help = 'Store each block this amount of times.')
  optparser.add_argument('-C', '--change-directory', metavar = 'DIR', help = 'Operate in given directory.')
  optparser.add_argument('-m', '--parallel', type = int, metavar = 'NUM', default = None, help = 'Count of workers to start (default: cpu count).')
  optparser.add_argument('-p', '--password', default = True, nargs = '?', metavar = 'PWD', help = 'Use this encryption password or ask for it.')

  optgroup2 = optparser.add_mutually_exclusive_group(required = False)
  optgroup2.add_argument('-z', '--gzip', type = int, default = None, metavar = 'LEVEL', help = 'Use GZip for compression.')
  optgroup2.add_argument('-j', '--bzip2', type = int, default = None, metavar = 'LEVEL', help = 'Use BZip2 for compression.')
  optgroup2.add_argument('-Z', '--lzma', type = int, default = None, metavar = 'LEVEL', help = 'Use LZMA for compression (default, level 9).')
  optgroup2.add_argument('-N', '--nocompress', action = 'store_true', help = 'Disable compression.')

  optgroup3 = optparser.add_mutually_exclusive_group(required = True)
  optgroup3.add_argument('-c', '--create', nargs = '+', metavar = 'FILE', help = 'Create an archive with given files.')
  optgroup3.add_argument('-x', '--extract', nargs = '*', metavar = 'FILE', help = 'Extract an archive fully or only given files.')
  optgroup3.add_argument('-t', '--list', nargs = '*', metavar = 'FILE', help = 'List an archive content fully or only given files.')
  optgroup3.add_argument('-s', '--search', nargs = '*', metavar = 'FILE', help = 'Search for an archive or list all archives.')
  optgroup3.add_argument('-k', '--list-keywords', action = 'store_true', help = 'List used keywords with usage count.')
  optgroup3.add_argument('--copy', nargs = '+', metavar = 'STORAGE', help = 'Copy an archive to other backend')

  presets = []
  for cfgfile in config_files:
    if os.path.exists(cfgfile):
      for conf in file(cfgfile):
        presets.extend(optparser.convert_arg_line_to_args(conf.strip()))
  options = optparser.parse_args(presets + args[1:])

  if (options.extract or options.list) \
      and not options.archive:
    sys.stderr.write("Please give an archive (-a) ID to operate.\n")
    sys.exit(1)

  if options.change_directory:
    os.chdir(options.change_directory)

  if options.redundancy < 1 or options.redundancy > len(options.storage):
    sys.stderr.write("Redundancy need to be between 1 and %d.\n" % len(options.storage))
    sys.exit(1)

  if options.lzma != None: compression = ('lzma', options.lzma)
  elif options.gzip != None: compression = ('gzip', options.gzip)
  elif options.bzip2 != None: compression = ('bzip2', options.bzip2)
  elif options.nocompress: compression = (None, 0)
  else: compression = ('lzma', 9)

  if compression[0] == None and password == None: parallel = None
  elif options.parallel == None:
    try:
      import multiprocessing
      parallel = multiprocessing.cpu_count()
    except: parallel = 1
  elif options.parallel < 1:
    sys.stderr.write("Parallization should be larger zero.\n")
    sys.exit(1)
  else: parallel = options.parallel

  if options.password == None:
    password = ''; verify = None
    while password != verify:
      password = getpass.unix_getpass(prompt = 'Password: ')
      verify   = getpass.unix_getpass(prompt = 'Verify:   ')
  elif options.password == True: password = None
  else: password = options.password

  return {
      'parser': optparser,
      'options': options,
      'compression': compression,
      'password': password,
      'parallel': parallel,
      'verbose': options.verbose,
      'redundancy': options.redundancy,
      'archive': options.archive,
      'storage': options.storage,
  }

def create_sub_backend(options, nimbstor, dir):
  if dir.startswith('imap:') or dir.startswith('imaps:'):
    proto, host, port, user, password, mailbox = dir.split(':', 6)
    port = int(port)
    from nimbstor.imap_backend import imap_backend
    return (imap_backend(nimbstor, user, password, host, mailbox, port,
                         proto == 'imaps', options['verbose']),
            "%s:%s:%d:%s::%s" % (proto, host, port, user, mailbox))
  elif dir.startswith('webdav:') or dir.startswith('webdavs:') :
    proto, host, port, user, password, basedir = dir.split(':', 6)
    port = int(port)
    if proto == 'webdav': urltype = 'http'
    else: urltype = 'https'
    from nimbstor.webdav_backend import webdav_backend
    return (webdav_backend(nimbstor, urltype, host, port, basedir, user, password, options['verbose']),
            "%s:%s:%s:%s::%s" % (proto, host, port, user, basedir))
  elif dir.startswith('sftp:'):
    proto, host, port, user, password, basedir = dir.split(':', 6)
    from nimbstor.sftp_backend import sftp_backend
    return (sftp_backend(nimbstor, host, port, basedir, user, password, options['verbose']),
            "%s:%s:%s:%s::%s" % (proto, host, port, user, basedir))
  from nimbstor.directory_backend import directory_backend
  return (directory_backend(nimbstor, dir, options['verbose']), dir)

def create_backend(options, nimbstor, storagelist):
  if len(storagelist) == 1:
    comb, name = create_sub_backend(options, nimbstor, storagelist[0])
    comb.activate()
    if options['verbose']:
        print "Use following backends:", name
    return comb
  namelist = []
  from nimbstor.combine_backend import combine_backend
  comb = combine_backend(nimbstor, options['redundancy'], options['verbose'])
  for dir in storagelist:
    x, n = create_sub_backend(options, comb, dir)
    x.activate()
    namelist.append(n)
  comb.activate()
  if options['verbose']:
    print "Use following backends:", ', '.join(namelist)
  return comb

def command_create_archive(options, start_time):
  """Create archive (tar -c)

  >>> os.system('rm -rf .nimbstor_parent out*/* || true')
  0
  >>> opt = command_tar_arguments(['test', '-v', '-p', 'qwer', '-m', '10', '-d', 'out1', 'out2', 'out3', '-D', 'test1', '-K', 'kwd1', '-c', 'f1', 'f2', 'f3'])
  >>> command_create_archive(opt, time.time())
  Use following backends: out1, out2, out3
  f1
  f2
  f3
  Archive ...

  """
  if not options['options'].desc:
    raise SystemError("Description must be given to create archive.")
  keywords = [x.lower().strip() for x in options['options'].keywords or []]
  desc = options['options'].desc.strip()
  output = stor_output(options['password'], options['compression'], options['archive'], desc, keywords, options['parallel'], not options['options'].empty, options['verbose'])
  try:
    create_backend(options, output, options['storage'])
    if os.path.exists('.nimbstor_parent'):
      parent = open('.nimbstor_parent').read().strip()
      if len(parent) == 64:
        if options['verbose']:
          print "Use parent", parent
        output.set_parent(parent)
    create_archive(output, options['options'].create, options['options'].verbose)
  finally: output.close()
  if output.archive() != None:
    open('.nimbstor_parent', 'w').write(output.archive())
  if options['verbose'] and output.archive() == None:
    print "No archive created."
  elif options['verbose']:
    print "Archive", output.archive(), "with size", output.size(), "created in", time.time() - start_time, "seconds."

def command_extract_archive(options, start_time):
  """Extract archive (tar -x)

  >>> archives = list(set([x[25:] for x in os.listdir('out1') if x.startswith('0000000.0000000000000000.')]))
  >>> opt = command_tar_arguments(['test', '-d', 'out1', 'out2', 'out3', '-p', 'qwer', '-v', '-a', archives[0], '-x'])
  >>> command_extract_archive(opt, time.time())
  Use following backends: out1, out2, out3
  f1
  f2
  f3
  Archive ...

  """
  input = stor_input(options['password'], options['archive'], options['parallel'], options['verbose'])
  try:
    create_backend(options, input, options['storage'])
    extract_archive(input, options['options'].extract, options['verbose'])
  finally: input.close()
  open('.nimbstor_parent', 'w').write(input.archive())
  if options['verbose']:
    print "Archive", options['archive'], "extracted in", time.time() - start_time, "seconds."

def command_list_archive(options, start_time):
  """List archive (tar -t)

  >>> archives = list(set([x[25:] for x in os.listdir('out1') if x.startswith('0000000.0000000000000000.')]))
  >>> opt = command_tar_arguments(['test', '-d', 'out1', 'out2', 'out3', '-p', 'qwer', '-a', archives[0], '-t'])
  >>> command_list_archive(opt, time.time())
  f1
  f2
  f3

  """
  input = stor_input(options['password'], options['archive'], options['parallel'], options['verbose'])
  try:
    create_backend(options, input, options['storage'])
    list_archive(input, options['options'].list, options['verbose'])
  finally: input.close()

def command_copy_archive(options, start_time):
  """Copy archive

  >>> archives = list(set([x[25:] for x in os.listdir('out1') if x.startswith('0000000.0000000000000000.')]))
  >>> opt = command_tar_arguments(['test', '-d', 'out3', '-p', 'qwer', '-a', archives[0], '-v', '--copy', 'out1', 'out2'])
  >>> command_copy_archive(opt, time.time())
  Use following backends: out3
  Use following backends: out1, out2
  Copy 2 blocks ...

  """
  input = stor_util(options['password'])
  try:
    create_backend(options, input, options['storage'])
    dest = stor_util(options['password'])
    try:
      create_backend(options, dest, options['options'].copy)
      copy_archive(input, dest, options['archive'], options['verbose'])
    finally: dest.close()
  finally: input.close()

def command_search_archive(options, start_time):
  """Search for archive

  >>> opt = command_tar_arguments(['test', '-d', 'out1', 'out2', 'out3', '-p', 'qwer', '-v', '-s'])
  >>> command_search_archive(opt, time.time())
  Use following backends: out1, out2, out3
  WEIGHT ARCHIVE                                      CREATED            SIZE           USAGE         DESCRIPTION
       0 ...

  """
  util = stor_util(options['password'])
  try:
    create_backend(options, util, options['storage'])
    search_archive(util, options['options'].search, options['verbose'])
  finally: util.close()

def command_list_keywords(options, start_time):
  """List used keywords.

  >>> opt = command_tar_arguments(['test', '-d', 'out1', 'out2', 'out3', '-p', 'qwer', '-v', '-k'])
  >>> command_list_keywords(opt, time.time())
  Use following backends: out1, out2, out3
  KEYWORD                        USAGE
  kwd1                           1   


  """
  util = stor_util(options['password'])
  create_backend(options, util, options['storage'])
  list_keywords(util, options['verbose'])


__all__ = (
    'create_archive',
    'extract_archive',
    'list_archive',
    'search_archive',
    'list_keywords',
    'copy_archive',
    'command_tar_arguments',
    'command_create_archive',
    'command_extract_archive',
    'command_list_archive',
    'command_copy_archive',
    'command_search_archive',
    'command_list_keywords',
)

# vim:sts=2:sw=2:
