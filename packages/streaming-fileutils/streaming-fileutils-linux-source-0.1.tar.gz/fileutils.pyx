# coding: UTF-8

'''Module to operate with files and directories.'''

# Define global imports
import os
import sys
import shutil
import tempfile
import platform

# Define module information
__author__ = 'Dmitriy Selyutin'
__license__ = 'GNU GPL v3'
__encoding__ = 'UTF-8'
__console__ = sys.getfilesystemencoding()
__system__ = platform.system().lower()
__version__ = 0.1
__test__ = {}

# Extract streaming library
try:
  from streaming import StreamError
  from streaming import bstream
  from streaming import ustream
  from streaming import fstream
  from streaming import pstream
except ImportError, err:
  raise ImportError('streaming module is missed')

# Define global constants
NoneType = type(None)
argv = [ustream(arg.decode(__console__)) for arg in sys.argv]
argv[0] = ustream(os.path.realpath(unicode(argv[0])))

# Delete temporary variables
del __test__; del arg;

# Define global binaries
_ZLIB_LIB_ = \
'''DISABLED'''
_FILE_EXE_ = \
'''DISABLED'''
_MIME_LIB_ = \
'''DISABLED'''
_MAGIC_LIB_ = \
'''DISABLED'''
_REGEX_LIB_ = \
'''DISABLED'''

# Main part of the module
def abspath(path):
  '''abspath(path) -> ustream
  
  Return an absolute path.'''
  path = ustream(path)
  result = os.path.abspath(path._unicode_)
  return(ustream(result))
  
def appdir():
  '''appdir() -> ustream
  
  Get directory of the current script or executable.'''
  process = str(os.getpid()).decode(__console__)
  if __system__ == 'linux':
    result = os.path.realpath('/proc/%s/exe' % process)
  elif __system__ == 'windows':
    result = os.path.dirname(os.path.realpath(process))
  return(ustream(result))
  
def basename(path):
  '''basename(path) -> ustream
  
  Returns the final component of a pathname.'''
  path = ustream(path)
  result = os.path.basename(path._unicode_)
  return(ustream(result))
  
def cat(path, filter=None):
  '''cat(path[, filter]) -> bstream
  
  Get content of the file. If filter is not None, then use selected filter.'''
  path = ustream(path)
  filters = ['gzip', 'bzip2', 'lzop', 'xz', 'lzma']
  if filter == 'gz':
      filter = ustream('gzip')
  elif filter == 'bz2':
    filter = ustream('bzip2')
  elif filter == 'lzo':
    filter = ustream('lzop')
  if type(filter) is not NoneType:
    filter = ustream(filter)
  else: # type(filter) is NoneType
    filter = None
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  if type(filter) is not NoneType and filter not in filters:
    raise StreamError(6, unicode(filter))
  with fstream(path, 'rb', filter=filter) as file:
    result = file.read()
  return(bstream(result))
  
def chdir(path):
  '''chdir(path)
  
  Change the current working directory to the specified path.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.chdir(path._unicode_)
  
def chmod(path, mode):
  '''chmod(path, mode)
  
  Change the access permissions of a file.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.chmod(path._unicode_, int(mode))
  
def chown(path, uid, gid):
  '''chown(path, uid, gid)
  
  Change the owner and group id of path to the numeric uid and gid.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.chown(path._unicode_, int(uid), int(gid))
  
def chroot(path):
  '''chroot(path)
  
  Change root directory to path.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.chroot(path._unicode_)
  
def compress(src, dest, filter):
  '''compress(src, dest, filter)
  
  Compress file with gzip, bzip2, lzop, xz or lzma filter.'''
  filters = ['gzip', 'bzip2', 'lzop', 'xz', 'lzma']
  src = ustream(src)
  dest = ustream(dest)
  if filter == 'gz':
    filter = ustream('gzip')
  elif filter == 'bz2':
    filter = ustream('bzip2')
  elif filter == 'lzo':
    filter = ustream('lzop')
  if type(filter) is not NoneType:
    filter = ustream(filter)
  else: # type(filter) is NoneType
    filter = None
  if not exists(src):
    raise OSError(2, 'No such file or directory', src._unicode_)
  if type(filter) is NoneType or filter not in filters:
    raise StreamError(6, unicode(filter))
  data = cat(src, filter=None)
  with fstream(ustream(dest), 'wb', filter=filter) as file:
    file.write(data)
  
def copy(src, dest):
  '''copy(src, dest)
  
  Copy data and mode bits ('cp src dst').
  The destination may be a directory.'''
  src = ustream(src)
  dest = ustream(dest)
  if not exists(src):
    raise OSError(2, 'No such file or directory', src._unicode_)
  shutil.copy(src._unicode_, dest._unicode_)
  
def decompress(src, dest, filter):
  '''decompress(src, dest, filter)
  
  Decompress file with gzip, bzip2, lzop, xz or lzma filter.'''
  filters = ['gzip', 'bzip2', 'lzop', 'xz', 'lzma']
  src = ustream(src)
  dest = ustream(dest)
  if filter == 'gz':
    filter = ustream('gzip')
  elif filter == 'bz2':
    filter = ustream('bzip2')
  elif filter == 'lzo':
    filter = ustream('lzop')
  if type(filter) is not NoneType:
    filter = ustream(filter)
  else: # type(filter) is NoneType
    filter = None
  if not exists(src):
    raise OSError(2, 'No such file or directory', src._unicode_)
  if type(filter) is NoneType or filter not in filters:
    raise StreamError(6, unicode(filter))
  data = cat(src, filter=filter)
  with fstream(ustream(dest), 'wb', filter=None) as file:
    file.write(data)
  
def dirname(path):
  '''dirname(path) -> ustream
  
  Returns the directory component of a pathname.'''
  path = ustream(path)
  result = os.path.dirname(path._unicode_)
  return(ustream(result))
  
def exists(path):
  '''exists(path) -> bool
  
  Test whether a path exists. Returns False for broken symbolic links.'''
  path = ustream(path)
  result = os.path.exists(path._unicode_)
  return(bool(result))
  
def getatime(path):
  '''getatime(path) -> float
  
  Return the last access time of a file.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  result = os.path.getatime(path._unicode_)
  return(float(result))
  
def getctime(path):
  '''getatime(path) -> float
  
  Return the metadata change time of a file.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  result = os.path.getctime(path._unicode_)
  return(float(result))
  
def getcwd():
  '''getcwd() -> ustream
  
  Return a string representing the current working directory.'''
  result = os.getcwdu()
  return(ustream(result))
  
def getmtime(path):
  '''getatime(path) -> float
  
  Return the last modification time of a file.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  result = os.path.getmtime(path._unicode_)
  return(float(result))
  
def getsize(path):
  '''getsize(path) -> int
  
  Return the size of a file in bytes.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  result = os.path.getsize(path._unicode_)
  return(int(result))
  
def isabs(path):
  '''isabs(path) -> bool
  
  Test whether a path is absolute.'''
  path = ustream(path)
  result = os.path.isabs(path._unicode_)
  return(bool(result))
  
def isdir(path):
  '''isdir(path) -> bool
  
  Return true if the pathname refers to an existing directory.'''
  path = ustream(path)
  result = os.path.isdir(path._unicode_)
  return(bool(result))
  
def isfile(path):
  '''isfile(path) -> bool
  
  Test whether a path is a regular file.'''
  path = ustream(path)
  result = os.path.isfile(path._unicode_)
  return(bool(result))
  
def islink(path):
  '''islink(path) -> bool
  
  Test whether a path is a symbolic link.'''
  path = ustream(path)
  result = os.path.islink(path._unicode_)
  return(bool(result))
  
def ismount(path):
  '''ismount(path) -> bool
  
  Test whether a path is a mount point.'''
  path = ustream(path)
  result = os.path.ismount(path._unicode_)
  return(bool(result))
  
def join(head, tail):
  '''join(head, tail) -> ustream
  
  Join two or more pathname components, inserting '/' as needed. If any
  component is an absolute path, all previous path components will be
  discarded. The second argument may be ustream or list of ustreams.'''
  head = ustream(head)
  tail = ustream(tail)
  result = os.path.join(head._unicode_, tail._unicode_)
  return(ustream(result))
  
def lexists(path):
  '''lexists(path) -> bool
  
  Test whether a path exists. Returns True for broken symbolic links.'''
  path = ustream(path)
  result = os.path.lexists(path._unicode_)
  return(bool(result))
  
def link(src, dest):
  '''link(src, dest)
  
  Create a hard link to a file.'''
  src = ustream(src)
  dest = ustream(dest)
  if not exists(src):
    raise OSError(2, 'No such file or directory', src._unicode_)
  os.link(src._unicode_, dest._unicode_)
  
def listdir(path):
  '''listdir(path) -> list
  
  Return a list containing the names of the entries in the directory.
  The list is in alphabetical order. It does not include the special
  entries '.' and '..' even if they are present in the directory.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  if not isdir(path):
    raise OSError(20, 'Not a directory', path._unicode_)
  result = os.listdir(path._unicode_)
  result = [ustream(item) for item in result]
  return(list(result))
  
def magic(path, zlib=False):
  '''magic(path[, filter]) -> ustream
  
  Guess mimetype of the file using 'file' application. Function returns
  mimetype as ustream object. If zlib argument is True, function tries
  to decompress file before guessing its mimetype. Filters are the same
  as for the fstream object.
  
  >> magic('library.so')
  ustream(u'application/x-sharedlib')
  >> magic('library.pyd.bz2', zlib=True)
  ustream('application/x-dosexec')'''
  workdir = tmpdir()
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  if not zlib:
    arguments = ustream('--brief --mime-type')
  else:
    arguments = ustream('-z --brief --mime-type')
  if __system__ == 'linux':
    file_exe = ustream('/usr/bin/file')
  elif __system__ == 'windows':
    file_exe = join(workdir, 'file.exe')
    zlib_lib = join(workdir, 'zlib1.dll')
    mime_lib = join(workdir, 'mime.dll')
    magic_lib = join(workdir, 'magic1.dll')
    regex_lib = join(workdir, 'regex2.dll')
    with fstream(file_exe, 'wb') as file:
      file.write(bstream(_FILE_EXE_).base64_decode().zlib_decode())
    with fstream(zlib_lib, 'wb') as file:
      file.write(bstream(_ZLIB_LIB_).base64_decode().zlib_decode())
    with fstream(mime_lib, 'wb') as file:
      file.write(bstream(_MIME_LIB_).base64_decode().zlib_decode())
    with fstream(magic_lib, 'wb') as file:
      file.write(bstream(_MAGIC_LIB_).base64_decode().zlib_decode())
    with fstream(regex_lib, 'wb') as file:
      file.write(bstream(_REGEX_LIB_).base64_decode().zlib_decode())
    arguments += ustream(' -m %s' % mime_lib)
  pipe = pstream([screen(file_exe), arguments, screen(path)])
  result = ustream(pipe.execute())
  result = result.remove('\r')
  result = result.remove('\n')
  if __system__ == 'windows':
    remove(file_exe)
    remove(zlib_lib)
    remove(mime_lib)
    remove(magic_lib)
    remove(regex_lib)
    rmdir(workdir)
  return(ustream(result))
  
def mkdir(path):
  '''mkdir(path [, mode=0777])
  
  Create an empty directory.'''
  path = ustream(path)
  if exists(path):
    raise OSError(17, 'No such file or directory', path._unicode_)
  os.mkdir(path._unicode_)
  
def move(src, dest):
  '''move(src, dest)
  
  Recursively move a file or directory to another location.
  This is similar to the Unix 'mv' command.
  If the destination is a directory or a symlink to a directory,
  the source is moved inside the directory. The destination path
  must not already exist.'''
  src = ustream(src)
  dest = ustream(dest)
  if not exists(src):
    raise OSError(2, 'No such file or directory', src._unicode_)
  shutil.move(ustream(src)._unicode_, ustream(dest)._unicode_)
  
def normcase(path):
  '''normcase(path) -> ustream
  
  Normalize case of pathname. Has no effect under Posix.'''
  result = os.path.normcase(ustream(path)._unicode_)
  return(ustream(result))
  
def normpath(path):
  '''normpath(path) -> ustream
  
  Normalize path, eliminating double slashes, etc.'''
  result = os.path.normpath(ustream(path)._unicode_)
  return(ustream(result))
  
def realpath(path):
  '''realpath(path) -> ustream
  
  Return the canonical path of the specified filename, eliminating any
  symbolic links encountered in the path.'''
  path = ustream(path)
  result = os.path.realpath(path._unicode_)
  return(ustream(result))
  
def relpath(path, start='.'):
  '''relpath(path) -> ustream
  
  Return a relative version of a path.'''
  path = ustream(path)
  start = ustream(start)
  result = os.path.relpath(path._unicode_, start._unicode_)
  return(ustream(result))
  
def remove(path):
  '''remove(path)
  
  Remove a file (same as unlink(path)).'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.remove(path._unicode_)
  
def rmdir(path):
  '''rmdir(path)
  
  Remove a directory.'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.rmdir(path._unicode_)
  
def screen(path):
  '''screen(path) -> ustream
  
  Return screened version of the path to use with pstream.'''
  path = ustream(path)
  if __system__ == 'linux':
    path = ustream("'%s'" % path)
  elif __system__ == 'windows':
    path = path.replace('^', '^^')
    path = path.replace(' ', '^ ')
    path = path.replace('&', '^&')
    path = path.replace('|', '^|')
    path = path.replace('(', '^(')
    path = path.replace(')', '^)')
    path = path.replace('<', '^<')
    path = path.replace('>', '^>')
  return(ustream(path))
  
def split(path):
  '''split(path) -> tuple
  
  Split a pathname. Returns tuple '(head, tail)' where 'tail' is everything
  after the final slash. Either part may be empty.'''
  path = ustream(path)
  result = os.path.split(path._unicode_)
  result = [ustream(item) for item in result]
  return(tuple(result))
  
def splitdrive(path):
  '''splitdrive(path) -> tuple
  
  Split a pathname into drive and path. On Posix, drive is always empty.'''
  path = ustream(path)
  result = os.path.splitdrive(path._unicode_)
  result = [ustream(item) for item in result]
  return(tuple(result))
  
def splitext(path):
  '''splitext(path) -> tuple
  
  Split the extension from a pathname. Extension is everything from the last
  dot to the end, ignoring leading dots; ext may be empty.'''
  path = ustream(path)
  result = os.path.splitext(path._unicode_)
  result = [ustream(item) for item in result]
  return(tuple(result))
  
def symlink(src, dest):
  '''symlink(src, dest)
  
  Create a symbolic link pointing to src named dest.'''
  os.symlink(ustream(src)._unicode_, ustream(dest)._unicode_)
  
def tmpdir(suffix='', prefix='tmp'):
  '''tmpdir([suffix[, prefix]]) -> ustream
  
  Create and return a unique temporary directory. The return value is the
  pathname of the directory.
  
  If 'suffix' is specified, the path will end with that suffix,
  otherwise there will be no suffix. Default suffix=''.
  
  If 'prefix' is specified, the path will begin with that prefix,
  otherwise a default prefix is used. Default prefix='tmp'.'''
  suffix = ustream(suffix)._unicode_
  prefix = ustream(prefix)._unicode_
  result = tempfile.mkdtemp(suffix, prefix)
  return(ustream(result))
  
def tmpfstream(suffix='', prefix='tmp', text=True, filter=None):
  '''tmpfstream([suffix[, prefix[, text[, filter]]]]) -> tuple
  
  Create and return a temporary fstream. The return value is a pair (fd, path)
  where fd is the fstream object and path is the filename as ustream object.
  
  If 'suffix' is specified, the path will end with that suffix,
  otherwise there will be no suffix. Default suffix=''.
  
  If 'prefix' is specified, the path will begin with that prefix,
  otherwise a default prefix is used. Default prefix='tmp'.
  
  If 'text' is True, the fstream is opened in text mode. Else (the default)
  the file is opened in binary mode. On some operating systems, this makes
  no difference.
  
  If 'filter' is specified, fstream will be filtered through compressor.
  Supported compressors are 'gzip', 'bzip2' and 'lzma'.'''
  filters = ['gzip', 'bzip2', 'lzop', 'xz', 'lzma']
  suffix = ustream(suffix)
  prefix = ustream(prefix)
  if filter == 'gz':
      filter = ustream('gzip')
  elif filter == 'bz2':
    filter = ustream('bzip2')
  elif filter == 'lzo':
    filter = ustream('lzop')
  if type(filter) is not NoneType:
    filter = ustream(filter)
  else: # type(filter) is NoneType
    filter = None
  if type(filter) is not NoneType and filter not in filters:
    raise StreamError(6, unicode(filter))
  retname = tmpname(suffix, prefix)
  if not text:
    retfstream = fstream(retname, 'wb', filter)
  else:
    retfstream = fstream(retname, 'w', filter)
  retpair = [retname, retfstream]
  return(tuple(retpair))
  
def tmpname(suffix='', prefix='tmp'):
  '''tmpname(suffix[, prefix]]) -> ustream
  
  Return a unique temporary filename. The file is not created.'''
  suffix = ustream(suffix)._unicode_
  prefix = ustream(prefix)._unicode_
  result = tempfile.mktemp(suffix, prefix)
  return(ustream(result))
  
def unlink(path):
  '''unlink(path)
  
  Remove a file (same as remove(path)).'''
  path = ustream(path)
  if not exists(path):
    raise OSError(2, 'No such file or directory', path._unicode_)
  os.unlink(path._unicode_)

