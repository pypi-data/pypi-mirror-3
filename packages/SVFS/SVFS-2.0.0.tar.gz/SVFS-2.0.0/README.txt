Simple Virtual File System 2.0 for Python 2.x.

Version: 2.0.0
API Revision: 1
Platform: Cross-platform
Author: Andrew Stolberg <andrewstolberg@gmail.com>

Table of contents

1.0 Introduction
2.0 API Reference

1.0 Introduction

SVFS allows to create virtual filesystem inside file on real filesystem. It can be used to store multiple files inside single file (with directory structure). Unlike archives, SVFS allows to modify files in-place. SVFS files use file-like interface, so they can be used (pretty much) like regular Python file objects. Finally, it's implemented in pure python and doesn't use any 3rd party modules, so it should be very portable.

SVFS doesn't support...

...file attributes.
...file permissions.
...working directory and relative pathnames.
...symlinks and multiple hardlinks.
...cached I/O.

Tests show write speed to be around 10-12 MB/s and read speed to be around 26-28 MB/s.

Safety notes:

1. You can't open more than one instance of same in-SVFS file. That was done to prevent data corruption.
2. Never try to open multiple instances of same SVFS. There is no cross-platform way to lock file, so opened SVFS is not locked, making it possible to open it from another instance or process. In most cases that will lead to undefined behavior and data loss.
3. Don't use threads with SVFS. In most cases that will lead to undefined behavior and data loss. It's not thread-safe. 

2.0 API Reference

 Note: Not all classes and methods and attributes are listed here. If you have good reason, you can figure out what they do yourself. If you don't, use documented ones.

 class SVFS.SVFS()

  This creates SVFS object. It doesn't accept any parameters.

  CreateSVFS(path,vnm,ftl,cml,csz[,rdn])

   Create new SVFS file. Returns 0.

   path - Path to SVFS file
   vnm - Name of volume
   ftl - Length of file table (first entry is always reserved for rootdir)
   cml - Length of cluster map
   csz - Size of cluster
   rdn - Name of rootdir

  CreateOpenRAMSVFS(vnm,ftl,cml,csz[,rdn])

   Create new SVFS in RAM and open it. Returns 0.

   vnm - Name of volume
   ftl - Length of file table (first entry is always reserved for rootdir)
   cml - Length of cluster map
   csz - Size of cluster
   rdn - Name of rootdir

  OpenSVFS(path)

   Open already existing SVFS file. Returns 0.

   path - Path to SVFS file

  CloseSVFS([store])

   Close opened SVFS. All opened in-SVFS files will be closed. Returns 0.

   store - Update mount/unmount timestamp

  RAMSVFSToSVFS(path[,chunksize])

   Store opened in-RAM SVFS into file. You can use specify chunksize for reading/writing operations (default is 4096 bytes). Returns 0.

   path - Path to SVFS file
   chunksize - Size of chunk for copying

  SVFSToRAMSVFS(path[,chunksize])

   Load SVFS from file into RAM and open it. You can use specify chunksize for reading/writing operations (default is 4096 bytes). Returns 0.

   path - Path to SVFS file
   chunksize - Size of chunk for copying

  open(name[,mode[,buffering]])

   Open file inside SVFS. Returns SVFSfile.

   name - Path to in-SVFS file
   mode - Mode string
   buffering - Dummy, has no effect

  opensf(name[,mode[,buffering]])

   Open file or special file inside SVFS. Returns SVFSfile.

   name - Path to in-SVFS file
   mode - Mode string
   buffering - Dummy, has no effect

  opensfe(name[,mode[,buffering]])

   Open special file inside SVFS. Returns SVFSfile.

   name - Path to in-SVFS file
   mode - Mode string
   buffering - Dummy, has no effect

  rmdir(path)

   Remove directory from SVFS. Only empty dirs can be deleted. Returns 0.

   path - Path to in-SVFS dir

  remove(path)

   Remove file from SVFS. Returns 0.

   path - Path to in-SVFS file

  removesf(path)

   Remove file or special file from SVFS. Returns 0.

   path - Path to in-SVFS file

  removesfe(path)

   Remove special file from SVFS. Returns 0.

   path - Path to in-SVFS file

  rename(src,dst)

   Rename/move file inside SVFS. Returns 0.

   src - Source path
   dst - Destination path

  renamesf(src,dst)

   Rename/move file or special inside SVFS. Returns 0.

   src - Source path
   dst - Destination path

  renamesfe(src,dst)

   Rename/move special file inside SVFS. Returns 0.

   src - Source path
   dst - Destination path

  copy(src,dst)

   Copy in-SVFS file. Returns 0.

   src - Source path
   dst - Destination path

  copysf(src,dst)

   Copy in-SVFS file or special file. Returns 0.

   src - Source path
   dst - Destination path

  copysfe(src,dst)

   Copy in-SVFS special file. Returns 0.

   src - Source path
   dst - Destination path

  getsize(path)

   Get size of file in bytes. Returns int.

   path - Path to in-SVFS file

  getsizestr(path)

   Get string with size of file. Returns string.

   path - Path to in-SVFS file

  getatime(path)

   Get access timestamp of file. Returns float.

   path - Path to in-SVFS file

  getmtime(path)

   Get modification timestamp of file. Returns float.

   path - Path to in-SVFS file

  getctime(path)

   Get creation timestamp of file. Returns float.

   path - Path to in-SVFS file

  setnormal(path)

   Set type of file to normal. Returns 0.

   path - Path to in-SVFS file

  setspecial(path)

   Set type of file to special. Returns 0.

   path - Path to in-SVFS file

  iscfile(path)

   Check if path is file or special file. Returns bool. If file doesn't exists, returns False too.

   path - Path to in-SVFS file

  issfile(path)

   Check if path is special file. Returns bool. If file doesn't exists, returns False too.

   path - Path to in-SVFS file

  isfile(path)

   Check if path is regular file. Returns bool. If file doesn't exists, returns False too.

   path - Path to in-SVFS file

  isdir(path)

   Check if path is dir or rootdir. Returns bool. If path doesn't exists, returns False too.

   path - In-SVFS path

  isrdir(path)

   Check if path is rootdir. Returns bool. If path doesn't exists, returns False too.

   path - In-SVFS path

  isndir(path)

   Check if path is dir. Returns bool. If path doesn't exists, returns False too.

   path - In-SVFS path

  exists(path)

   Check if path exists (special files ignored). Returns bool.

   path - In-SVFS path

  existssf(path)

   Check if path exists. Returns bool.

   path - In-SVFS path

  existssfe(path)

   Check if special file exists. Returns bool.

   path - In-SVFS path

  mknod(filename[,mode[,device]])

   Create file inside SVFS.

   filename - In-SVFS path
   mode - Dummy, has no effect
   device - Zero value creates regular file, otherwise creates special file

  mkdir(filename[,mode])

   Create dir inside SVFS.

   path - In-SVFS path
   mode - Dummy, has no effect

  listdir(path)

   Return list of files and directories (special files ignored).

   path - In-SVFS path

  listdirsf(path)

   Return list of files and directories.

   path - In-SVFS path

  listdirsfe(path)

   Return list of special files.

   path - In-SVFS path

  dirname(path)

   Return dir name of path.

   path - In-SVFS path

  getsvfssizestr()

   Return string containing SVFS container size.

  getsvfsfreestr()

   Return string containing remaining free space in SVFS.

  getsvfsspacestr()

   Return string containing actual storage capacity of SVFS.

  getsvfssize()

   Return SVFS container size in bytes.

  getsvfsfree()

   Return remaining free space in SVFS in bytes.

  getsvfsspace()

   Return actual storage capacity of SVFS in bytes.

  fstat(fd)

   Return os.stat like info. Takes inode number.

   fd - Number of inode

  fstatvfs(fd)

   Return description of filesystem (like os.statvfs). Takes inode number.

   fd - Number of inode

  stat(path)

   Return os.stat like info. Takes path.

   path - In-SVFS path

  statvfs(path)

   Return description of filesystem (like os.statvfs). Takes path.

   path - In-SVFS path

  getsvfsstats(md,ftbl,cmap)

   Deprecated function to get filesystem stats. Use statvfs instead.

   md - Instance of Metadata
   ftbl - File table (list of FTEntry)
   cmap - Cluster map (list of CMEntry)

  convert_bytes(bytes)

   Convert bytes to string with appropriate units (KB, MB, GB, etc.).

 class SVFS.SVFS.SVFSfile()

  Creates new SVFS file object. Never create instances of SVFSfile manually, use open function of SVFS class instead. Supports for loops and with statements.

  xreadlines()

   Returns same thing as iter(f).

  readlines([sizehint])

   Reads lines from file until EOF and returns list of strings.

   sizehint - if specified, reads until total byte size of lines read is more than or equal to sizehint instead of reading until EOF.

  readline([size])

   Read single line from file. Keeps newlines, but if file ends with incomplete line, newline may be absent.

   size - Maximum line length in bytes (including newlines). If line length reaches size, an incomplete line will be returned.

  next()

   Return next line from file. Raises StopIteration if reached EOF.

  read([size])

   Read bytes from file until EOF reached.

   size - If specified, reads at most this amount of bytes. If EOF reached, it may return less bytes.

  writelines(sequence)

   Write sequence (list, tuple, other iterables) of strings to file.

   sequence - Iterable object, producing strings

  write(str_)

   Write single string to file.

   str_ - String to write

  seek(offset[,whence])

   Seek to position in file.

   offset - Position to seek to
   whence - If not specified or 0 - seek to absolute position. If 1 - seek relatively to current position. If 2 - seek relatively to file's end.

  tell()

   Get current position in file.

  isatty()

   Always returns False, because files not connected to tty.

  fileno()

   Returns file's inode number.

  flush()

   Nop, since SVFS doesn't support buffered I/O.

  truncate([size])

   Truncate file's size. Size defaults to current position.

   size - If specified, file is truncated to that size. If specified size exceeds current size, file will be unchanged.

  close()

   Close file. Any operations on closed file will fail.

  mode

   Read-only attribute, containing file's mode.

  softspace

   Writable attribute, needed for print statement.

  newlines

   Read-only attribute. None if no newlines found, '\r', '\n', '\r\n' or tuple containing all newline types found.

  name

   Read-only attribute, containing file's path.

  errors

   None, there is no Unicode error handler.

  encoding

   None.

  closed

   Bool, indicating whether file is closed or not.
