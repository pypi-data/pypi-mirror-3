#SVFS 2.0 - Simple Virtual File System
#Both simple and powerful virtual file system, written in pure python.
#
#  Copyright (C) 2012 Andrew Stolberg
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import os,sys,struct,datetime,time,io,weakref

class SVFS(object):
 
 class SVFSError(Exception):
  def __init__(self, code, msg):
   self.code = code
   self.msg = msg
  def __str__(self):
   return '[Errno ' + str(self.code) + '] ' + self.msg

 class SVFSIOError(Exception):
  def __init__(self, code, msg):
   self.code = code
   self.msg = msg
  def __str__(self):
   return '[Errno ' + str(self.code) + '] ' + self.msg

 class Identifier(object):

  def __init__(self,idb='VFS2'):
   self.idb = idb

  def tofile(self,f):
   if len(self.idb) > 4:
    self.idb = self.idb[0:4]
   if len(self.idb) < 4:
    self.idb + '\x00' * (4 - len(self.idb))
   f.write(self.idb)
   return 0

  def fromfile(self,f):
   self.idb = f.read(4)
   return 0

 class Metadata (object):

  def __init__(self,vnm='',ftl=0,cml=0,csz=1,rev=0):
   self.vnm = vnm
   self.ftl = ftl
   self.cml = cml
   self.csz = csz
   self.rev = rev
   if self.csz < 1:
    self.csz = 1

  def tofile(self,f):
   f.write(struct.pack('<256p',self.vnm))
   f.write(struct.pack('<L',self.ftl))
   f.write(struct.pack('<L',self.cml))
   f.write(struct.pack('<H',self.csz-1))
   f.write(struct.pack('<B',self.rev))
   return 0

  def fromfile(self,f):
   self.vnm = struct.unpack('<256p',f.read(256))[0]
   self.ftl = struct.unpack('<L',f.read(4))[0]
   self.cml = struct.unpack('<L',f.read(4))[0]
   self.csz = struct.unpack('<H',f.read(2))[0] + 1
   self.rev = struct.unpack('<B',f.read(1))[0]
   return 0

 class FTEntry(object):

  def __init__(self,fnm='',typ=0,pnt=0,fcl=0,cts=0.0,ats=0.0,wts=0.0,fsz=0):
   self.fnm = fnm
   self.typ = typ
   self.pnt = pnt
   self.fcl = fcl
   self.cts = cts
   self.ats = ats
   self.wts = wts
   self.fsz = fsz

  def tofile(self,f):
   self.fnm = self.fnm.replace('/','')
   f.write(struct.pack('<256p',self.fnm))
   f.write(struct.pack('<B',self.typ))
   f.write(struct.pack('<L',self.pnt))
   f.write(struct.pack('<L',self.fcl))
   f.write(struct.pack('<d',self.cts))
   f.write(struct.pack('<d',self.ats))
   f.write(struct.pack('<d',self.wts))
   f.write(struct.pack('<Q',self.fsz))
   return 0

  def fromfile(self,f):
   self.fnm = struct.unpack('<256p',f.read(256))[0]
   self.typ = struct.unpack('<B',f.read(1))[0]
   self.pnt = struct.unpack('<L',f.read(4))[0]
   self.fcl = struct.unpack('<L',f.read(4))[0]
   self.cts = struct.unpack('<d',f.read(8))[0]
   self.ats = struct.unpack('<d',f.read(8))[0]
   self.wts = struct.unpack('<d',f.read(8))[0]
   self.fsz = struct.unpack('<Q',f.read(8))[0]
   return 0

 class CMEntry(object):

  def __init__(self,val=0):
   self.val = val

  def tofile(self,f):
   f.write(struct.pack('<L',self.val))
   return 0

  def fromfile(self,f):
   self.val = struct.unpack('<L',f.read(4))[0]
   return 0

 class Cluster(object):

  def __init__(self,size=1):
   if size < 1:
    size = 1
   if size > 65536:
    size = 65536
   self.size = size
   self.data = bytearray(size)

  def tofile(self,f):
   f.write(self.data)
   return 0

  def fromfile(self,f):
   self.data = bytearray(f.read(self.size))
   return 0

 class SVFSstats(object):

  def __init__(self):
   self.clustersize = 0
   self.clustercount = 0
   self.clusterfree = 0
   self.filescount = 0
   self.filesfree = 0
   self.maxnamelength = 0

 class SVFSaltstats(object):

  def __init__(self):
   self.f_bsize = 0
   self.f_frsize = 0
   self.f_blocks = 0
   self.f_bfree = 0
   self.f_bavail = 0
   self.f_files = 0
   self.f_ffree = 0
   self.f_favail = 0
   self.f_flag = 0
   self.f_namemax = 0

  def __getitem__(self,i):
   if i == 0:
    return self.f_bsize
   elif i == 1:
    return self.f_frsize
   elif i == 2:
    return self.f_blocks
   elif i == 3:
    return self.f_bfree
   elif i == 4:
    return self.f_bavail
   elif i == 5:
    return self.f_files
   elif i == 6:
    return self.f_ffree
   elif i == 7:
    return self.f_favail
   elif i == 8:
    return self.f_flag
   elif i == 9:
    return self.f_namemax
   else:
    raise IndexError('Tuple index out of range')

 class SVFSpathstats(object):

  def __init__(self):
   self.st_mode = 0
   self.st_ino = 0
   self.st_dev = 0
   self.st_nlink = 0
   self.st_uid = 0
   self.st_gid = 0
   self.st_size = 0
   self.st_atime = 0
   self.st_mtime = 0
   self.st_ctime = 0
   self.st_obtype = 0

  def __getitem__(self,i):
   if i == 0:
    return self.st_mode
   elif i == 1:
    return self.st_ino
   elif i == 2:
    return self.st_dev
   elif i == 3:
    return self.st_nlink
   elif i == 4:
    return self.st_uid
   elif i == 5:
    return self.st_gid
   elif i == 6:
    return self.st_size
   elif i == 7:
    return self.st_atime
   elif i == 8:
    return self.st_mtime
   elif i == 9:
    return self.st_ctime
   else:
    raise IndexError('Tuple index out of range')

 class SVFSfile(object):

  def __init__(self):
   self._path = ''
   self._mode = 0
   self._pos = 0
   self._info = None
   self._cchain = None
   self._encoding = None
   self._errors = None
   self._newlines = None
   self._softspace = 0
   self._parent = None
   self._closed = None
   self._fentry = None

  def close(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   self._closed = True
   return 0

  @property
  def closed(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   return self._closed

  @property
  def encoding(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   return self._encoding

  @property
  def errors(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   return self._errors

  @property
  def name(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   return self._path

  @property
  def newlines(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   return self._newlines

  @property
  def softspace(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   return self._softspace

  @softspace.setter
  def softspace(self,value):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if not isinstance(value,int):
    raise ValueError('Not an integer')
   self._softspace = value

  @property
  def mode(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._mode == 1:
    return 'rb'
   if self._mode == 2:
    return 'rb+'
   if self._mode == 3:
    return 'wb'
   if self._mode == 4:
    return 'wb+'
   if self._mode == 5:
    return 'ab'
   if self._mode == 6:
    return 'ab+'
   self._mode = 1
   return 'rb'

  def truncate(self,size=-1):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if self._mode not in (2,3,4,5,6):
    raise self._parent.SVFSIOError(1,'File not open for writing')
   if size < 0:
    size = self._pos
   try:
    chg = []
    if self._info.fsz <= size:
     return 0
    count = size / self._parent.meta.csz
    if size % self._parent.meta.csz > 0:
     count += 1
    cchg = False
    while len(self._cchain) > count:
     cchg = True
     if len(self._cchain) > 1:
      self._parent.cmap[self._cchain[len(self._cchain)-1]].val = 0
      self._parent.cmap[self._cchain[len(self._cchain)-2]].val = 1
      chg.append(self._cchain[len(self._cchain)-1])
      chg.append(self._cchain[len(self._cchain)-2])
      del self._cchain[len(self._cchain)-1]
     else:
      self._parent.cmap[self._cchain[len(self._cchain)-1]].val = 0
      chg.append(self._cchain[len(self._cchain)-1])
      del self._cchain[len(self._cchain)-1]
      self._info.fcl = 0
    self._info.fsz = size
    index = self._fentry
    self._parent.seekftbln(self._parent.svfs,index)
    self._parent.ftbl[index].tofile(self._parent.svfs)
    if cchg:
     chg = set(chg)
     self._parent.updateclustermap(self._parent.svfs,self._parent.meta,self._parent.cmap,chg)
    return 0
   except:
    raise RuntimeError('Unknown error')

  def flush(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return 0

  def fileno(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return self._fentry

  def isatty(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return False

  def tell(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return self._pos

  def seek(self,offset,whence=0):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if whence == 0:
    if offset >= 0:
     self._pos = offset
     return 0
    else:
     raise self._parent.SVFSIOError(0,'Negative seek offset')
   elif whence == 1:
    if self._pos + offset >= 0:
     self._pos += offset
     return 0
    else:
     raise self._parent.SVFSIOError(0,'Negative seek offset')
   elif whence == 2:
    if self._info.fsz + offset >= 0:
     self._pos += self._info.fsz + offset
     return 0
    else:
     raise self._parent.SVFSIOError(0,'Negative seek offset')
   raise ValueError('Bad argument')

  def write(self,str_):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if self._mode not in (2,3,4,5,6):
    raise self._parent.SVFSIOError(1,'File not open for writing')
   if self._mode in (5,6):
    self._pos = self._info.fsz
   if not isinstance(str_,str):
    try:
     str(str_)
    except:
     raise ValueError('Buffer error')
   chg = []
   wbuf = len(str_)
   clus = 0
   count = wbuf
   wbufd = count
   fsz = self._info.fsz
   nfsz = self._pos + count
   if nfsz > fsz:
    fsz = nfsz
   clusi = self._pos / self._parent.meta.csz
   cluso = self._pos % self._parent.meta.csz
   script = []
   if fsz % self._parent.meta.csz > 0:
    tmp2 = True
   else:
    tmp2 = False
   if len(self._cchain) < ((fsz / self._parent.meta.csz) + tmp2):
    stats = self._parent.getsvfsstats(self._parent.meta,self._parent.ftbl,self._parent.cmap)
    if stats.clusterfree < (((fsz / self._parent.meta.csz) + tmp2) - len(self._cchain)):
     raise self._parent.SVFSError(9,'Not enough free disk space to perform operation')
    else:
     if (len(self._cchain)) > 0:
      tmp = (((fsz / self._parent.meta.csz) + tmp2) - (len(self._cchain)))
     else:
      tmp = (((fsz / self._parent.meta.csz) + tmp2))
     while tmp > 0:
      tmp -= 1
      script.append((2,))
   script.append((1,clusi,cluso))
   recl = self._parent.meta.csz - cluso
   if recl > count:
    recl = count
   count -= recl
   pbuf = 0
   script.append((0,pbuf,recl))
   pbuf += recl
   while count > 0:
    clus += 1
    script.append((1,clusi + clus,0))
    if count >= self._parent.meta.csz:
     recl = self._parent.meta.csz
    elif count < self._parent.meta.csz:
     recl = fsz % self._parent.meta.csz
    elif count > self._parent.meta.csz:
     count = self._parent.meta.csz
    count -= recl
    script.append((0,pbuf,recl))
    pbuf += recl
   offset = 0
   clstrbuf = self._parent.Cluster(self._parent.meta.csz)
   cchg = False
   for i in script:
    if i[0] == 0:
     clstrbuf.data[offset:offset + i[2]] = str_[i[1]:i[1]+i[2]+1]
     clstrbuf.tofile(self._parent.svfs)
    if i[0] == 1:
     self._parent.seekclstnmd(self._parent.svfs,self._parent.meta,self._cchain[i[1]])
     offset = i[2]
     clstrbuf.fromfile(self._parent.svfs)
     self._parent.seekclstnmd(self._parent.svfs,self._parent.meta,self._cchain[i[1]])
    if i[0] == 2:
     cchg = True
     tmp = self._parent.getfreeclstr(self._parent.meta,self._parent.cmap)
     if len(self._cchain) != 0:
      if self._parent.cmap[self._cchain[len(self._cchain) - 1]].val == 1:
        self._parent.cmap[self._cchain[len(self._cchain) - 1]].val = tmp + 2
        self._parent.cmap[tmp].val = 1
        chg.append(self._cchain[len(self._cchain) - 1])
        chg.append(tmp)
        self._cchain.append(tmp)
     else:
      self._parent.cmap[tmp].val = 1
      self._cchain.append(tmp)
      self._info.fcl = tmp
      chg.append(tmp)
   self._info.ats = time.mktime(datetime.datetime.now().timetuple())
   self._info.wts = time.mktime(datetime.datetime.now().timetuple())
   self._info.fsz = fsz
   index = self._fentry
   self._parent.seekftbln(self._parent.svfs,index)
   self._parent.ftbl[index].tofile(self._parent.svfs)
   if cchg:
    chg = set(chg)
    self._parent.updateclustermap(self._parent.svfs,self._parent.meta,self._parent.cmap,chg)
   self._pos = self._pos + wbufd
   return 0

  def writelines(self,sequence):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   for i in sequence:
    if not isinstance(i,str):
     raise ValueError('Sequence of strings required')
   for i in sequence:
    try:
     self.write(i)
    except:
     raise self._parent.SVFSIOError(3,'Write failed')
   return 0

  def read(self,size=-1):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if self._mode not in (1,2,4,6):
    raise self._parent.SVFSIOError(2,'File not open for reading')
   if size == 0:
    return ''
   clus = 0
   fsz = self._info.fsz
   if size > 0:
    nfsz = self._pos + size
    if nfsz > fsz:
     nfsz = fsz
    size = nfsz - self._pos
   if size < 0:
    size = fsz - self._pos
   if size <= 0:
    return ''
   wbuf = size
   bfr = bytearray(wbuf)
   clusi = self._pos / self._parent.meta.csz
   cluso = self._pos % self._parent.meta.csz
   script = []
   script.append((1,clusi,cluso))
   recl = self._parent.meta.csz - cluso
   if recl > size:
    recl = size
   size -= recl
   pbuf = 0
   script.append((0,pbuf,recl))
   pbuf += recl
   while size > 0:
    clus += 1
    script.append((1,clusi + clus,0))
    if size >= self._parent.meta.csz:
     recl = self._parent.meta.csz
    elif size < self._parent.meta.csz:
     recl = fsz % self._parent.meta.csz
    size -= recl
    script.append((0,pbuf,recl))
    pbuf += recl
   offset = 0
   clstrbuf = self._parent.Cluster(self._parent.meta.csz)
   for i in script:
    if i[0] == 0:
     clstrbuf.fromfile(self._parent.svfs)
     bfr[i[1]:i[1]+i[2]] = clstrbuf.data[offset:offset+i[2]]
    if i[0] == 1:
     self._parent.seekclstnmd(self._parent.svfs,self._parent.meta,self._cchain[i[1]])
     offset = i[2]
     clstrbuf.fromfile(self._parent.svfs)
     self._parent.seekclstnmd(self._parent.svfs,self._parent.meta,self._cchain[i[1]])
   self._info.ats = time.mktime(datetime.datetime.now().timetuple())
   index = self._fentry
   self._parent.seekftbln(self._parent.svfs,index)
   self._parent.ftbl[index].tofile(self._parent.svfs)
   self._pos = self._pos + wbuf
   return str(bfr)

  def __iter__(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return self

  def __enter__(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return self

  def __exit__(self, exc_type, exc_val, exc_tb):
   try:
    return self.close()
   except:
    raise self._parent.SVFSError(2,'SVFS is not opened')

  def __del__(self):
   try:
    self.close()
   except:
    pass

  def next(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if self._mode not in (1,2,4,6):
    raise self._parent.SVFSIOError(2,'File not open for reading')
   while 1:
    ret = self.readline()
    if not ret:
     raise StopIteration
    else:
     return ret

  def readline(self,size=-1):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if self._mode not in (1,2,4,6):
    raise self._parent.SVFSIOError(2,'File not open for reading')
   if size == 0:
    return ''
   bfr = ''
   tmp = ''
   chunksize = self._parent.meta.csz
   if size < 0:
    size = self._info.fsz - self._pos
    if size <= 0:
     return ''
   wpos = self._pos
   wcount = size
   length = 0
   newl = None
   end = False
   while not end:
    if wcount == 0:
     break
    if wcount > chunksize:
     tmp = self.read(chunksize)
    else:
     tmp = self.read(wcount)
    if not tmp:
     break
    wcount -= len(tmp)
    i = tmp.find('\n')
    if i != -1:
     bfr += tmp
     length += i+1
     newl = '\n'
     end = True
     break
    i = tmp.find('\r')
    if i != -1:
     if i == len(tmp) - 1:
      tmp2 = self.read(1)
      if not tmp2:
       bfr += tmp
       length += i+1
       end = True
       break
      elif tmp2[0] == '\n':
       bfr += tmp+tmp2
       length += i+2
       newl = '\r\n'
       end = True
       break
      else:
       bfr += tmp
       length += i+1
       newl = '\r'
       end = True
       break
     else:
      if tmp[i+1] == '\n':
       bfr += tmp+tmp2
       length += i+2
       newl = '\r\n'
       end = True
       break
      else:
       bfr += tmp
       length += i+1
       newl = '\r'
       end = True
       break
    if not end:
     bfr += tmp
     length += len(tmp)
   bfr = bfr[0:length]
   self.seek(wpos + length)
   if newl is not None:
    if self._newlines is None:
     self._newlines = newl
    if isinstance(self._newlines,str) and self._newlines != newl:
     self._newlines = (self._newlines,newl)
    if isinstance(self._newlines,tuple) and newl not in self._newlines:
     self._newlines = self._newlines + (newl,)
   return str(bfr)

  def readlines(self,sizehint=-1):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   if self._mode not in (1,2,4,6):
    raise self._parent.SVFSIOError(2,'File not open for reading')
   if sizehint == 0:
    return []
   if sizehint < 0:
    sizehint = self._info.fsz
   if sizehint == 0:
    return []
   length = 0
   ret = []
   for i in self:
    length += len(i)
    ret.append(i)
    if length >= sizehint:
     return ret
   return ret

  def xreadlines(self):
   if not self._parent.opened:
    raise self._parent.SVFSError(2,'SVFS is not opened')
   if self._closed:
    raise ValueError('I/O operation on closed file')
   return iter(self)

 def __init__(self):
  self.opened = False
  self.svfs = None
  self.path = None
  self.ident = None
  self.meta = None
  self.ftbl = None
  self.cmap = None
  self.files = []
  self.currev = 1
  self.type = 0

 def convert_bytes(self,bytes):
  suffixes = (' bytes',' KB',' MB',' GB',' TB',' PB',' EB',' ZB',' YB')
  bytes = float(bytes)
  sval = 0
  while bytes > 1024:
   sval += 1
   bytes = bytes / 1024
  if sval > 8:
   raise ValueError('Value is too high')
  return ('%.2f' % bytes) + suffixes[sval]

 def seekident(self,f):
  f.seek(0)
  return 0

 def seekmetad(self,f):
  f.seek(4)
  return 0

 def seekftble(self,f):
  f.seek(4 + 267)
  return 0

 def seekftbln(self,f,n):
  f.seek(4 + 267 + (297 * n))
  return 0

 def seekclmap(self,f,ftl):
  f.seek(4 + 267 + (297 * ftl))
  return 0

 def seekcmapn(self,f,ftl,n):
  f.seek(4 + 267 + (297 * ftl) + (4 * n))
  return 0

 def seekclust(self,f,ftl,cml):
  f.seek(4 + 267 + (297 * ftl) + (4 * cml))
  return 0

 def seekclstn(self,f,ftl,cml,csz,n):
  f.seek(4 + 267 + (297 * ftl) + (4 * cml) + (csz * n))
  return 0

 def seekfseof(self,f,ftl,cml,csz):
  f.seek(4 + 267 + (297 * ftl) + (4 * cml) + (csz * cml))
  return 0

 def seekclmapmd(self,f,md):
  f.seek(4 + 267 + (297 * md.ftl))
  return 0

 def seekcmapnmd(self,f,md,n):
  f.seek(4 + 267 + (297 * md.ftl) + (4 * n))
  return 0

 def seekclustmd(self,f,md):
  f.seek(4 + 267 + (297 * md.ftl) + (4 * md.cml))
  return 0

 def seekclstnmd(self,f,md,n):
  f.seek(4 + 267 + (297 * md.ftl) + (4 * md.cml) + (md.csz * n))
  return 0

 def seekfseofmd(self,f,md):
  f.seek(4 + 267 + (297 * md.ftl) + (4 * md.cml) + (md.csz * md.cml))
  return 0

 def ftblcreate(self,length):
  ftbl = []
  while length > 0:
   length -= 1
   ftbl.append(self.FTEntry())
  return ftbl

 def ftbltofile(self,f,ftbl):
  for i in ftbl:
   i.tofile(f)
  return 0

 def ftblfromfile(self,f,ftbl):
  for i in ftbl:
   i.fromfile(f)
  return 0

 def cmapcreate(self,length):
  cmap = []
  while length > 0:
   length -= 1
   cmap.append(self.CMEntry())
  return cmap

 def cmaptofile(self,f,cmap):
  for i in cmap:
   i.tofile(f)
  return 0

 def cmapfromfile(self,f,cmap):
  for i in cmap:
   i.fromfile(f)
  return 0

 def getfreefile(self,md,ftbl):
  for i in xrange(md.ftl):
   if ftbl[i].typ == 0:
    return i
  raise self.SVFSError(0,'File table is full')

 def countfreefiles(self,md,ftbl):
  cnt = 0
  for i in ftbl:
   if i.typ == 0:
    cnt += 1
  return cnt

 def getfreeclstr(self,md,cmap):
  for i in xrange(md.cml):
   if cmap[i].val == 0:
    return i
  raise self.SVFSError(1,'Disk is full')

 def countfreeclstr(self,md,cmap):
  cnt = 0
  for i in cmap:
   if i.val == 0:
    cnt += 1
  return cnt

 def getsvfsstats(self,md,ftbl,cmap):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  stats = self.SVFSstats()
  stats.clustersize = md.csz
  stats.clustercount = md.cml
  stats.clusterfree = self.countfreeclstr(md,cmap)
  stats.filescount = md.ftl
  stats.filesfree = self.countfreefiles(md,ftbl)
  stats.maxnamelength = 255
  return stats

 def statvfs(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  if self.followpath(self.ftbl,path) == -1:
   raise self.SVFSError(3,'No such file or directory')
  stats = self.SVFSaltstats()
  stats.f_bsize = self.meta.csz
  stats.f_frsize = self.meta.csz
  stats.f_blocks = self.meta.cml
  stats.f_bfree = self.countfreeclstr(self.meta,self.cmap)
  stats.f_bavail = stats.f_bfree
  stats.f_files = self.meta.ftl
  stats.f_ffree = self.countfreefiles(self.meta,self.ftbl)
  stats.f_favail = stats.f_ffree
  stats.f_flag = 0
  stats.f_namemax = 255
  return stats

 def stat(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  frec = self.followpath(self.ftbl,path)
  if frec == -1:
   raise self.SVFSError(3,'No such file or directory')
  stats = self.SVFSpathstats()
  stats.st_mode = 0
  if self.ftbl[frec].typ in (2,4):
   stats.st_mode = stats.st_mode | 0040000
  if self.ftbl[frec].typ == 3:
   stats.st_mode = stats.st_mode | 0060000
  if self.ftbl[frec].typ == 1:
   stats.st_mode = stats.st_mode | 0100000
  stats.st_ino = frec
  if self.ftbl[frec].typ == 3:
   stats.st_dev = 1
  else:
   stats.st_dev = 0
  stats.st_nlink = 1
  stats.st_uid = 0
  stats.st_gid = 0
  stats.st_size = self.ftbl[frec].fsz
  stats.st_atime = self.ftbl[frec].ats
  stats.st_mtime = self.ftbl[frec].wts
  stats.st_ctime = self.ftbl[frec].cts
  stats.st_obtype = self.ftbl[frec].typ
  return stats

 def fstatvfs(self,fd):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if fd >= 0 and fd < self.meta.ftl:
   if self.meta.fself.ftbl[fd].typ == 0:
    raise self.SVFSError(3,'No such file or directory')
  else:
   raise self.SVFSError(3,'No such file or directory')
  stats = self.SVFSaltstats()
  stats.f_bsize = self.meta.csz
  stats.f_frsize = self.meta.csz
  stats.f_blocks = self.meta.cml
  stats.f_bfree = self.countfreeclstr(self.meta,self.cmap)
  stats.f_bavail = stats.f_bfree
  stats.f_files = self.meta.ftl
  stats.f_ffree = self.countfreefiles(self.meta,self.ftbl)
  stats.f_favail = stats.f_ffree
  stats.f_flag = 0
  stats.f_namemax = 255
  return stats

 def fstat(self,fd):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if fd >= 0 and fd < self.meta.ftl:
   if self.meta.fself.ftbl[fd].typ == 0:
    raise self.SVFSError(3,'No such file or directory')
  else:
   raise self.SVFSError(3,'No such file or directory')
  stats = self.SVFSpathstats()
  stats.st_mode = 0
  if self.ftbl[frec].typ in (2,4):
   stats.st_mode = stats.st_mode | 0040000
  if self.ftbl[frec].typ == 3:
   stats.st_mode = stats.st_mode | 0060000
  if self.ftbl[frec].typ == 1:
   stats.st_mode = stats.st_mode | 0100000
  stats.st_ino = frec
  if self.ftbl[frec].typ == 3:
   stats.st_dev = 1
  else:
   stats.st_dev = 0
  stats.st_nlink = 1
  stats.st_uid = 0
  stats.st_gid = 0
  stats.st_size = self.ftbl[frec].fsz
  stats.st_atime = self.ftbl[frec].ats
  stats.st_mtime = self.ftbl[frec].wts
  stats.st_ctime = self.ftbl[frec].cts
  stats.st_obtype = self.ftbl[frec].typ
  return stats

 def getsvfsspace(self):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  return self.meta.cml * self.meta.csz

 def getsvfsfree(self):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  return self.meta.csz * self.countfreeclstr(self.meta,self.cmap)

 def getsvfssize(self):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  return 4 + 267 + (297 * self.meta.ftl) + (4 * self.meta.cml) + ((self.meta.csz) * self.meta.csz)

 def getsvfsspacestr(self):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  return self.convert_bytes(self.meta.cml * self.meta.csz)

 def getsvfsfreestr(self):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  return self.convert_bytes(self.meta.csz * self.countfreeclstr(self.meta,self.cmap))

 def getsvfssizestr(self):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  return self.convert_bytes(4 + 267 + (297 * self.meta.ftl) + (4 * self.meta.cml) + ((self.meta.csz) * self.meta.csz))

 def getfiles(self, ftbl, fnm=None, typ=None, pnt=None, fcl=None, cts=None, ats=None, wts=None, fsz=None):
  res = []
  cnt = -1
  for i in ftbl:
   cnt += 1
   mfnm = False
   mtyp = False
   mpnt = False
   mfcl = False
   mcts = False
   mats = False
   mwts = False
   mfsz = False
   if fnm is None:
    mfnm = True
   elif i.fnm == fnm:
    mfnm = True
   if typ is None:
    mtyp = True
   elif i.typ == typ:
    mtyp = True
   if pnt is None:
    mpnt = True
   elif i.pnt == pnt:
    mpnt = True
   if fcl is None:
    mfcl = True
   elif i.fcl == fcl:
    mfcl = True
   if cts is None:
    mcts = True
   elif i.cts == cts:
    mcts = True
   if ats is None:
    mats = True
   elif i.ats == ats:
    mats = True
   if wts is None:
    mwts = True
   elif i.wts == wts:
    mwts = True
   if fsz is None:
    mfsz = True
   elif i.fsz == fsz:
    mfsz = True
   if mfnm and mtyp and mpnt and mfcl and mcts and mats and mwts and mfsz:
    res.append(cnt)
  return res

 def getfilesalt(self, ftbl, fnm=None, typ=None, pnt=None, fcl=None, cts=None, ats=None, wts=None, fsz=None):
  res = []
  cnt = -1
  for i in ftbl:
   cnt += 1
   mfnm = False
   mtyp = False
   mpnt = False
   mfcl = False
   mcts = False
   mats = False
   mwts = False
   mfsz = False
   if fnm is None:
    mfnm = True
   elif i.fnm in fnm:
    mfnm = True
   if typ is None:
    mtyp = True
   elif i.typ in typ:
    mtyp = True
   if pnt is None:
    mpnt = True
   elif i.pnt in pnt:
    mpnt = True
   if fcl is None:
    mfcl = True
   elif i.fcl in fcl:
    mfcl = True
   if cts is None:
    mcts = True
   elif i.cts in cts:
    mcts = True
   if ats is None:
    mats = True
   elif i.ats in ats:
    mats = True
   if wts is None:
    mwts = True
   elif i.wts in wts:
    mwts = True
   if fsz is None:
    mfsz = True
   elif i.fsz in fsz:
    mfsz = True
   if mfnm and mtyp and mpnt and mfcl and mcts and mats and mwts and mfsz:
    res.append(cnt)
  return res

 def getfirst(self, ftbl, fnm=None, typ=None, pnt=None, fcl=None, cts=None, ats=None, wts=None, fsz=None):
  cnt = -1
  for i in ftbl:
   cnt += 1
   mfnm = False
   mtyp = False
   mpnt = False
   mfcl = False
   mcts = False
   mats = False
   mwts = False
   mfsz = False
   if fnm is None:
    mfnm = True
   elif i.fnm in fnm:
    mfnm = True
   if typ is None:
    mtyp = True
   elif i.typ in typ:
    mtyp = True
   if pnt is None:
    mpnt = True
   elif i.pnt in pnt:
    mpnt = True
   if fcl is None:
    mfcl = True
   elif i.fcl in fcl:
    mfcl = True
   if cts is None:
    mcts = True
   elif i.cts in cts:
    mcts = True
   if ats is None:
    mats = True
   elif i.ats in ats:
    mats = True
   if wts is None:
    mwts = True
   elif i.wts in wts:
    mwts = True
   if fsz is None:
    mfsz = True
   elif i.fsz in fsz:
    mfsz = True
   if mfnm and mtyp and mpnt and mfcl and mcts and mats and mwts and mfsz:
    return cnt
  return -1

 def parsepath(self,path):
  if len(path) != 0:
   if path[0] == '/':
    path = path[1:]
  if len(path) != 0:
   if path[-1] == '/':
    path = path[:-1]
  return path.split('/')

 def dirname(self,path):
  if len(path) != 0:
   if path[0] == '/':
    path = path[1:]
  if len(path) != 0:
   if path[-1] == '/':
    path = path[:-1]
  path = path.split('/')
  if len(path) > 1:
   return '/' + '/'.join(path[0:len(path)-1])
  if len(path) == 1:
   return '/'
  return '/'

 def followpath(self,ftbl,path):
  if path in ['','/']:
   path = self.ftbl[0].fnm
  path = self.parsepath(path)
  if path is None: raise ValueError('Bad path')
  parent = 0
  found = False
  ret = 0
  for i in xrange(len(path)):
   ret = self.getfirst(ftbl,fnm=path[i],typ=(1,2,3,4),pnt=(parent,))
   if ret != -1:
    parent = ret
    if i == len(path) - 1:
     return parent
    found = True
   if not found:
    return -1
   found = False

 def pathtonodelist(self,ftbl,path):
  if path in ['','/']:
   path = self.ftbl[0].fnm
  path = self.parsepath(path)
  if path is None: raise ValueError('Bad path')
  parent = 0
  nodes = []
  found = False
  ret = 0
  for i in xrange(len(path)):
   ret = self.getfirst(ftbl,fnm=path[i],typ=(1,2,3,4),pnt=(parent,))
   if ret != -1:
    parent = ret
    nodes.append(parent)
    if i == len(path) - 1:
     return nodes
    found = True
   if not found:
    return -1
   found = False

 def getclusterchain(self,cmap,fcl):
  clus = fcl + 2
  res = []
  end = False
  while not end:
   try:
    clus = clus - 2
    if (clus >= 0) and (clus < len(cmap)) and (cmap[clus].val >= 0) and (cmap[clus].val-2 < len(cmap)):
     if clus not in res:
      res.append(clus)
     else:
      raise ValueError('Circular reference in cluster chain')
     clus = cmap[clus].val
     if clus == 1:
      return res
     if clus == 0:
      raise ValueError('Reference to free cluster')
    else:
     raise ValueError('Reference is out of range')
   except:
    raise RuntimeError('Unknown error')

 def writefiletable(self,f,ftbl):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  self.seekftble(f)
  self.ftbltofile(f,ftbl)
  return True

 def writeclustermap(self,f,md,cmap):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  self.seekclmapmd(f,md)
  self.cmaptofile(f,cmap)
  return True

 def updatefiletable(self,f,ftbl,chglist):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  for i in chglist:
   self.seekftbln(f,i)
   ftbl[i].tofile(f)
  return True

 def updateclustermap(self,f,md,cmap,chglist):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  for i in chglist:
   self.seekcmapnmd(f,md,i)
   cmap[i].tofile(f)
  return True

 def readfiletable(self,f,ftbl):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  self.seekftble(f)
  self.ftblfromfile(f,ftbl)
  return True

 def readclustermap(self,f,md,cmap):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  self.seekclmapmd(f,md)
  self.cmapfromfile(f,cmap)
  return True

 def _listdirback(self,path,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  foldi = self.followpath(self.ftbl,path)
  if foldi == -1:
   raise self.SVFSError(3,'No such file or directory')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  if sf:
   tmp = self.getfilesalt(self.ftbl,pnt=(foldi,),typ=(1,2,3))
  elif sf == 2:
   tmp = self.getfilesalt(self.ftbl,pnt=(foldi,),typ=(3,))
  else:
   tmp = self.getfilesalt(self.ftbl,pnt=(foldi,),typ=(1,2))
  res = []
  for i in tmp:
   res.append(self.ftbl[i].fnm)
  return res

 def listdir(self,path):
  return self._listdirback(path,False)

 def listdirsf(self,path):
  return self._listdirback(path,True)

 def listdirsfe(self,path):
  return self._listdirback(path,2)

 def mkdir(self,path,mode=0):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  stats = self.getsvfsstats(self.meta,self.ftbl,self.cmap)
  if stats.filesfree < 1:
   raise self.SVFSError(0,'File table is full')
  folder = self.dirname(path)
  fnm = self.parsepath(path)
  fnm = fnm[len(fnm) - 1]
  if folder in ['','/']:
   folder = self.ftbl[0].fnm
  if fnm == '' or '/' in fnm or len(fnm) > 255:
   raise ValueError('Bad filename')
  foldi = self.followpath(self.ftbl,folder)
  if foldi == -1:
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[foldi].typ not in (2,4):
   raise self.SVFSError(4,'Not a directory')
  tmp = self.getfiles(self.ftbl,fnm=fnm,pnt=foldi)
  if len(tmp) != 0:
   raise self.SVFSError(5,'Conflicting filename')
  fentry = self.getfreefile(self.meta,self.ftbl)
  self.ftbl[fentry].fnm = fnm
  self.ftbl[fentry].typ = 2
  self.ftbl[fentry].pnt = foldi
  self.ftbl[fentry].fcl = 0
  self.ftbl[fentry].cts = time.mktime(datetime.datetime.now().timetuple())
  self.ftbl[fentry].ats = time.mktime(datetime.datetime.now().timetuple())
  self.ftbl[fentry].wts = time.mktime(datetime.datetime.now().timetuple())
  self.ftbl[fentry].fsz = 0
  self.seekftbln(self.svfs,fentry)
  self.ftbl[fentry].tofile(self.svfs)
  return 0

 def _fcreateback(self,path,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  stats = self.getsvfsstats(self.meta,self.ftbl,self.cmap)
  if stats.filesfree < 1:
   raise self.SVFSError(0,'File table is full')
  folder = self.dirname(path)
  fnm = self.parsepath(path)
  fnm = fnm[len(fnm) - 1]
  if folder in ['','/']:
   folder = self.ftbl[0].fnm
  if fnm == '' or '/' in fnm or len(fnm) > 255:
   raise ValueError('Bad filename')
  foldi = self.followpath(self.ftbl,folder)
  if foldi == -1:
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[foldi].typ not in (2,4):
   raise self.SVFSError(4,'Not a directory')
  tmp = self.getfiles(self.ftbl,fnm=fnm,pnt=foldi)
  if len(tmp) != 0:
   raise self.SVFSError(5,'Conflicting filename')
  fentry = self.getfreefile(self.meta,self.ftbl)
  self.ftbl[fentry].fnm = fnm
  if sf:
   self.ftbl[fentry].typ = 3
  else:
   self.ftbl[fentry].typ = 1
  self.ftbl[fentry].pnt = foldi
  self.ftbl[fentry].fcl = 0
  self.ftbl[fentry].cts = time.mktime(datetime.datetime.now().timetuple())
  self.ftbl[fentry].ats = time.mktime(datetime.datetime.now().timetuple())
  self.ftbl[fentry].wts = time.mktime(datetime.datetime.now().timetuple())
  self.ftbl[fentry].fsz = 0
  self.seekftbln(self.svfs,fentry)
  self.ftbl[fentry].tofile(self.svfs)
  return 0

 def mknod(self,filename,mode=0,device=0):
  if device == 0:
   return self._fcreateback(filename,False)
  else:
   return self._fcreateback(filename,True)

 def _fexistsback(self,path,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  else:
   if sf:
    if self.ftbl[chk].typ not in (1,2,3,4):
     return False
   if sf == 2:
    if self.ftbl[chk].typ not in (3,):
     return False
   else:
    if self.ftbl[chk].typ not in (1,2,4):
     return False
   return True

 def exists(self,path):
  return self._fexistsback(path,sf=False)

 def existssf(self,path):
  return self._fexistsback(path,sf=True)

 def existssfe(self,path):
  return self._fexistsback(path,sf=2)

 def isfile(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  elif self.ftbl[chk].typ == 1:
   return True
  return False

 def isdir(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  elif self.ftbl[chk].typ in (2,4):
   return True
  return False

 def isrdir(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  elif self.ftbl[chk].typ == 4:
   return True
  return False

 def isndir(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  elif self.ftbl[chk].typ == 2:
   return True
  return False

 def issfile(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  elif self.ftbl[chk].typ == 3:
   return True
  return False

 def iscfile(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   return False
  elif self.ftbl[chk].typ in (1,3):
   return True
  return False

 def setspecial(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[chk].typ == 1:
   self.ftbl[chk].typ = 3
   self.seekftbln(self.svfs,chk)
   self.ftbl[chk].tofile(self.svfs)
  return 0

 def setnormal(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[chk].typ == 3:
   self.ftbl[chk].typ = 1
   self.seekftbln(self.svfs,chk)
   self.ftbl[chk].tofile(self.svfs)
  return 0

 def getatime(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  else:
   return self.ftbl[chk].ats

 def getmtime(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  else:
   return self.ftbl[chk].wts

 def getctime(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  else:
   return self.ftbl[chk].cts

 def getsize(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  else:
   return self.ftbl[chk].fsz

 def getsizestr(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  chk = self.followpath(self.ftbl,path)
  if chk == -1:
   raise self.SVFSError(3,'No such file or directory')
  else:
   return self.convert_bytes(self.ftbl[chk].fsz)

 def _fcopyback(self,src,dst,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if src in ['','/']:
   src = self.ftbl[0].fnm
  if dst in ['','/']:
   dst = self.ftbl[0].fnm
  frec = self.followpath(self.ftbl,src)
  if frec == -1:
   raise self.SVFSError(3,'No such file or directory')
  tmp = self.followpath(self.ftbl,dst)
  if tmp != -1:
   raise self.SVFSError(7,'File already exists')
  if sf:
   if self.ftbl[frec].typ not in (1,3):
    raise self.SVFSError(3,'No such file or directory')
  elif sf == 2:
   if self.ftbl[frec].typ != 3:
    raise self.SVFSError(3,'No such file or directory')
  else:
   if self.ftbl[frec].typ != 1:
    raise self.SVFSError(3,'No such file or directory')
  self.cleanupweak()
  for i in self.files:
   nfpth = i()._fentry
   if nfpth != -1 and frec == nfpth and not i()._closed:
    raise self.SVFSError(17,'Only one instance of file can be opened at same time')
  f1 = self.open(src,'r')
  f2 = self.open(dst,'w')
  while 1:
   data = f1.read(self.meta.csz)
   if not data:
    break
   f2.write(data)
  f1.close()
  f2.close()
  self.cleanupweak()
  if self.ftbl[frec].typ == 3:
   self.setspecial(dst)
  return 0

 def copy(self,src,dst):
  return self._fcopyback(src,dst,sf=False)

 def copysf(self,src,dst):
  return self._fcopyback(src,dst,sf=True)

 def copysfe(self,src,dst):
  return self._fcopyback(src,dst,sf=2)

 def _fmoveback(self,old,new,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if old in ['','/']:
   old = self.ftbl[0].fnm
  if new in ['','/']:
   new = self.ftbl[0].fnm
  frec = self.followpath(self.ftbl,old)
  if frec == -1:
   raise self.SVFSError(3,'No such file or directory')
  if sf:
   if self.ftbl[frec].typ not in (1,2,3,4):
    raise self.SVFSError(3,'No such file or directory')
  elif sf == 2:
   if self.ftbl[frec].typ not in (3,):
    raise self.SVFSError(3,'No such file or directory')
  else:
   if self.ftbl[frec].typ not in (1,2,4):
    raise self.SVFSError(3,'No such file or directory')
  self.cleanupweak()
  for i in self.files:
   nlst = self.pathtonodelist(self.ftbl,i()._path)
   if isinstance(nlst,list):
    if frec in nlst and not i()._closed:
     raise self.SVFSError(6,'File or directory busy')
  folder1 = self.dirname(old)
  if folder1 in ['','/']:
   folder1 = self.ftbl[0].fnm
  drec1 = self.followpath(self.ftbl,folder1)
  folder2 = self.dirname(new)
  if folder2 in ['','/']:
   folder2 = self.ftbl[0].fnm
  drec2 = self.followpath(self.ftbl,folder2)
  if drec1 == -1 or drec2 == -1:
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[frec].typ == 4:
   if drec != drec2:
    raise ValueError('Both files should be in same directory')
  if self.ftbl[frec].typ in (2,4):
   if self.getfirst(self.ftbl,pnt=(folder1,),typ=(1,2,3,4)) != -1:
    raise self.SVFSError(12,'Directory is not empty')
  fnm = self.parsepath(new)
  fnm = fnm[len(fnm) - 1]
  if fnm == '' or '/' in fnm or len(fnm) > 255:
   raise ValueError('Bad filename')
  if self.getfirst(self.ftbl,fnm=(fnm,),pnt=drec2,typ=(1,2,3,4)) != -1:
   raise self.SVFSError(7,'File already exists')
  self.ftbl[frec].fnm = fnm
  self.ftbl[frec].pnt = drec2
  if self.ftbl[frec].typ in (2,4):
   self.ftbl[frec].wts = time.mktime(datetime.datetime.now().timetuple())
  self.seekftbln(self.svfs,frec)
  self.ftbl[frec].tofile(self.svfs)
  return 0

 def rename(self,src,dst):
  return self._fmoveback(src,dst,False)

 def renamesf(self,src,dst):
  return self._fmoveback(src,dst,True)

 def renamesfe(self,src,dst):
  return self._fmoveback(src,dst,2)

 def cleanupweak(self):
  for i in reversed(xrange(len(self.files))):
   if self.files[i]() is None:
    del self.files[i]
  return 0

 def _fremoveback(self,path,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  fentry = self.followpath(self.ftbl,path)
  if fentry == -1:
   raise self.SVFSError(3,'No such file or directory')
  if sf:
   if self.ftbl[fentry].typ not in (1,3):
    raise self.SVFSError(3,'No such file or directory')
  elif sf == 2:
   if self.ftbl[fentry].typ != 3:
    raise self.SVFSError(3,'No such file or directory')
  else:
   if self.ftbl[fentry].typ != 1:
    raise self.SVFSError(3,'No such file or directory')
  self.cleanupweak()
  for i in self.files:
   nfpth = self.followpath(self.ftbl,i()._path)
   if nfpth != -1:
    try:
     if fentry == nfpth and not i()._closed:
      raise self.SVFSError(6,'File or directory busy')
    except AttributeError:
     pass
    except:
     raise
   try:
    tmp = self.open(path,'w')
    tmp.close()
    tmp = None
   except:
    raise self.SVFSIOError(4,'Failed to truncate file')
  self.seekftbln(self.svfs,fentry)
  tmp2 = self.FTEntry()
  tmp2.tofile(self.svfs)
  self.ftbl[fentry] = tmp2
  return 0

 def remove(self,path):
  return self._fremoveback(path,False)

 def removesf(self,path):
  return self._fremoveback(path,True)

 def removesfe(self,path):
  return self._fremoveback(path,2)

 def rmdir(self,path):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  fentry = self.followpath(self.ftbl,path)
  if fentry == -1:
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[fentry].typ not in (2,4):
   raise self.SVFSError(3,'No such file or directory')
  if self.ftbl[fentry].typ == 4:
   raise self.SVFSError(18,'Cannot delete rootdir')
  if self.getfirst(self.ftbl,fnm=(fnm,),pnt=drec2,typ=(1,2,3,4)) != -1:
   raise self.SVFSError(12,'Directory is not empty')
  self.seekftbln(self.svfs,fentry)
  tmp2 = self.FTEntry()
  tmp2.tofile(self.svfs)
  self.ftbl[fentry] = tmp2
  return 0

 def _fopenback(self,path,mode,sf=False):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if mode in ('r','rb'):
   mode = 1
  elif mode in ('r+','r+b','rb+'):
   mode = 2
  elif mode in ('w','wb'):
   mode = 3
  elif mode in ('w+','w+b','wb+'):
   mode = 4
  elif mode in ('a','ab'):
   mode = 5
  elif mode == ('a+','a+b','ab+'):
   mode = 6
  else:
   raise ValueError('Bad mode')
  if path in ['','/']:
   path = self.ftbl[0].fnm
  fref = self.SVFSfile()
  fref._mode = mode
  fref._path = path
  fref._pos = 0
  fref._closed = False
  fref._parent = self
  fref._info = self.followpath(self.ftbl,path)
  fref._fentry = fref._info
  frec = fref._info
  self.cleanupweak()
  for i in self.files:
   nfpth = i()._fentry
   if nfpth != -1 and fref._info == nfpth and not i()._closed:
    raise self.SVFSError(17,'Only one instance of file can be opened at same time')
  created = False
  if fref._info == -1:
   if mode in (3,4,5,6):
    try:
     self._fcreateback(path,sf)
    except:
     fref = None
     raise self.SVFSError(8,"Couldn't create file")
    created = True
    fref._info = self.followpath(self.ftbl,path)
    frec = fref._info
    fref._fentry = frec
    if fref._info == -1:
     fref = None
     raise self.SVFSError(8,"Couldn't create file")
   else:
    fref = None
    raise self.SVFSError(3,'No such file or directory')
  fref._info = self.ftbl[fref._info]
  fref._info.ats = time.mktime(datetime.datetime.now().timetuple())
  if sf:
   if fref._info.typ not in (1,3):
    fref = None
    raise self.SVFSError(3,'No such file or directory')
  elif sf == 2:
   if fref._info.typ != 3:
    fref = None
    raise self.SVFSError(3,'No such file or directory')
  else:
   if fref._info.typ != 1:
    fref = None
    raise self.SVFSError(3,'No such file or directory')
  if fref._info.fsz == 0:
   fref._cchain = []
  else:
   try:
    fref._cchain = self.getclusterchain(self.cmap,fref._info.fcl)
   except:
    fref = None
    raise ValueError('Bad cluster chain')
  if mode in (3,4) and not created:
   try:
    fref.truncate(0)
   except:
    fref = None
    raise self.SVFSIOError(4,'Failed to truncate file')
  if mode in (5,6):
   fref._pos = fref._info.fsz
  self.seekftbln(self.svfs,frec)
  self.ftbl[frec].tofile(self.svfs)
  self.files.append(weakref.ref(fref))
  return fref

 def open(self,name,mode='r',buffering=None):
  return self._fopenback(name,mode,False)

 def opensf(self,name,mode='r',buffering=None):
  return self._fopenback(name,mode,True)

 def opensfe(self,name,mode='r',buffering=None):
  return self._fopenback(name,mode,2)

 def CreateSVFS(self,path,vnm,ftl,cml,csz,rdn='#ROOTDIR#'):
  if (len(vnm) > 255) or (ftl < 1) or (ftl > 4294967296) or (cml < 1) or (cml > 4294967294) or (csz > 65536) or (csz < 1):
   raise ValueError('Bad argument')
  if rdn == '' or '/' in rdn or len(rdn) > 255:
   raise ValueError('Bad argument')
  svfssize = 4 + 267 + (297 * ftl) + (4 * cml) + ((csz) * cml)
  dchk = True
  try:
   diskfree = os.statvfs(os.path.dirname(path))
   diskfree = diskfree.f_frsize * diskfree.f_bfree
  except:
   dchk = False
  if dchk:
   if diskfree < svfssize:
    raise self.SVFSError(9,'Not enough free disk space to perform operation')
  try:
   svfs = open(path,'wb')
  except IOError:
   raise self.SVFSError(10,"Couldn't open file")
  try:
   tmp = self.Identifier()
   tmp.tofile(svfs)
   tmp = self.Metadata(vnm,ftl,cml,csz,self.currev)
   tmp.tofile(svfs)
   tmp = self.ftblcreate(ftl)
   tmp[0] = self.FTEntry(rdn,4,0,0,time.mktime(datetime.datetime.now().timetuple()),time.mktime(datetime.datetime.now().timetuple()),time.mktime(datetime.datetime.now().timetuple()),0)
   self.ftbltofile(svfs,tmp)
   tmp = self.cmapcreate(cml)
   self.cmaptofile(svfs,tmp)
   tmp = self.Cluster(csz)
   cml = cml
   while cml > 0:
    cml -= 1
    tmp.tofile(svfs)
   tmp = None
   svfs.close()
  except IOError:
   svfs.close()
   raise self.SVFSIOError(3,'Write failed')
  return 0

 def CreateOpenRAMSVFS(self,vnm,ftl,cml,csz,rdn='#ROOTDIR#'):
  if (len(vnm) > 255) or (ftl < 1) or (ftl > 4294967296) or (cml < 1) or (cml > 4294967294) or (csz > 65536) or (csz < 1):
   raise ValueError('Bad argument')
  if rdn == '' or '/' in rdn or len(rdn) > 255:
   raise ValueError('Bad argument')
  try:
   self.svfs = io.BytesIO()
   self.path = '#RAM#'
   self.type = 2
   tmp = self.Identifier()
   tmp.tofile(self.svfs)
   tmp = self.Metadata(vnm,ftl,cml,csz,self.currev)
   tmp.tofile(self.svfs)
   tmp = self.ftblcreate(ftl)
   tmp[0] = self.FTEntry(rdn,4,0,0,time.mktime(datetime.datetime.now().timetuple()),time.mktime(datetime.datetime.now().timetuple()),time.mktime(datetime.datetime.now().timetuple()),0)
   self.ftbltofile(self.svfs,tmp)
   tmp = self.cmapcreate(cml)
   self.cmaptofile(self.svfs,tmp)
   tmp = self.Cluster(csz)
   cml = cml
   while cml > 0:
    cml -= 1
    tmp.tofile(self.svfs)
   tmp = None
   self.svfs.seek(0)
   self.ident = self.Identifier()
   self.ident.fromfile(self.svfs)
   self.meta = self.Metadata()
   self.meta.fromfile(self.svfs)
   self.ftbl = self.ftblcreate(self.meta.ftl)
   self.ftblfromfile(self.svfs,self.ftbl)
   self.cmap = self.cmapcreate(self.meta.cml)
   self.cmapfromfile(self.svfs,self.cmap)
   self.opened = True
   self.ftbl[0].ats = time.mktime(datetime.datetime.now().timetuple())
   self.seekftbln(self.svfs,0)
   self.ftbl[0].tofile(self.svfs)
   return 0
  except:
   raise RuntimeError('Unknown error')

 def OpenSVFS(self,path):
  fsize = os.path.getsize(path)
  if fsize < 573:
   self.CloseSVFS()
   raise self.SVFSError(13,'File is corrupted or not a valid SVFS volume (file is too small)')
  try:
   svfs = open(path,'rb+',0)
   self.path = path
  except IOError:
   self.CloseSVFS()
   raise self.SVFSError(10,"Couldn't open file")
  self.type = 1
  try:
   self.svfs = svfs
   self.ident = self.Identifier()
   self.ident.fromfile(svfs)
   if self.ident.idb != 'VFS2':
    self.CloseSVFS()
    raise self.SVFSError(14,'File is corrupted or not a valid SVFS volume (bad identifier)')
   self.meta = self.Metadata()
   self.meta.fromfile(svfs)
   if (len(self.meta.vnm) > 255) or (self.meta.ftl < 1) or (self.meta.ftl > 4294967296) or (self.meta.cml < 1) or (self.meta.cml > 4294967294) or (self.meta.csz > 65536) or (self.meta.csz < 1) or (self.meta.rev != self.currev):
    self.CloseSVFS()
    raise self.SVFSError(15,'File is corrupted or not a valid SVFS volume (bad metadata block)')
   fsizei = 4 + 267 + (297 * self.meta.ftl) + (4 * self.meta.cml) + ((self.meta.cml) * self.meta.csz)
   if fsize != fsizei:
    self.CloseSVFS()
    raise self.SVFSError(16,'File is corrupted or not a valid SVFS volume (invalid file size)')
   self.ftbl = self.ftblcreate(self.meta.ftl)
   self.ftblfromfile(svfs,self.ftbl)
   self.cmap = self.cmapcreate(self.meta.cml)
   self.cmapfromfile(svfs,self.cmap)
   self.opened = True
   if self.ftbl[0].typ != 4 or self.ftbl[0].fnm == '' or '/' in self.ftbl[0].fnm or len(self.ftbl[0].fnm) > 255:
    raise ValueError('Bad rootdir entry')
   else:
    self.ftbl[0].ats = time.mktime(datetime.datetime.now().timetuple())
    self.seekftbln(self.svfs,0)
    self.ftbl[0].tofile(self.svfs)
  except IOError:
   self.CloseSVFS()
   raise self.SVFSIOError(5,'Read failed')
  return 0

 def CloseSVFS(self,store=True):
  try:
   if not self.svfs.closed and store:
    try:
     self.ftbl[0].ats = time.mktime(datetime.datetime.now().timetuple())
     self.seekftbln(self.svfs,0)
     self.ftbl[0].tofile(self.svfs)
    except:
     pass
   self.cleanupweak()
   for i in self.files:
    if i() is not None:
     if not i()._closed:
      i().close()
   self.svfs.close()
   self.opened = False
   self.svfs = None
   self.path = None
   self.ident = None
   self.meta = None
   self.ftbl = None
   self.cmap = None
   self.files = []
   self.type = 0
  except:
   raise RuntimeError('Unknown error')
  return 0

 def RAMSVFSToSVFS(self,path,chunksize=4096):
  if not self.opened:
   raise self.SVFSError(2,'SVFS is not opened')
  if self.type != 2:
   raise ValueError('Bad SVFS mode')
  try:
   tmp = open(path,'w')
   self.svfs.seek(0)
   if chunksize <= 0:
    chunksize = 4096
   while 1:
    tmp2 = self.svfs.read(chunksize)
    if not tmp2:
     break
    else:
     tmp.write(tmp2)
   tmp.close()
   return 0
  except:
   raise RuntimeError('Unknown error')

 def SVFSToRAMSVFS(self,path,chunksize=4096):
  fsize = os.path.getsize(path)
  if fsize < 573:
   self.CloseSVFS()
   raise self.SVFSError(13,'File is corrupted or not a valid SVFS volume (file is too small)')
  if self.opened:
   raise self.SVFSError(11,'SVFS is opened')
  try:
   tmp = open(path,'r',0)
  except IOError:
   self.CloseSVFS()
   raise self.SVFSError(10,"Couldn't open file")
  try:
   svfs = io.BytesIO()
   if chunksize <= 0:
    chunksize = 4096
   while 1:
    tmp2 = tmp.read(chunksize)
    if not tmp2:
     break
    else:
     svfs.write(tmp2)
  except:
   self.CloseSVFS()
   raise self.SVFSIOError(6,'Read/Write failed')
  svfs.seek(0)
  self.path = '#RAM#'
  self.type = 2
  try:
   self.svfs = svfs
   self.ident = self.Identifier()
   self.ident.fromfile(svfs)
   if self.ident.idb != 'VFS2':
    self.CloseSVFS()
    raise self.SVFSError(14,'File is corrupted or not a valid SVFS volume (bad identifier)')
   self.meta = self.Metadata()
   self.meta.fromfile(svfs)
   if (len(self.meta.vnm) > 255) or (self.meta.ftl < 1) or (self.meta.ftl > 4294967296) or (self.meta.cml < 1) or (self.meta.cml > 4294967294) or (self.meta.csz > 65536) or (self.meta.csz < 1) or (self.meta.rev != self.currev):
    self.CloseSVFS()
    raise self.SVFSError(15,'File is corrupted or not a valid SVFS volume (bad metadata block)')
   fsizei = 4 + 267 + (297 * self.meta.ftl) + (4 * self.meta.cml) + ((self.meta.cml) * self.meta.csz)
   if fsize != fsizei:
    self.CloseSVFS()
    raise self.SVFSError(16,'File is corrupted or not a valid SVFS volume (invalid file size)')
   self.ftbl = self.ftblcreate(self.meta.ftl)
   self.ftblfromfile(svfs,self.ftbl)
   self.cmap = self.cmapcreate(self.meta.cml)
   self.cmapfromfile(svfs,self.cmap)
   self.opened = True
   if self.ftbl[0].typ != 4 or self.ftbl[0].fnm == '' or '/' in self.ftbl[0].fnm or len(self.ftbl[0].fnm) > 255:
    raise ValueError('Bad rootdir entry')
   else:
    self.ftbl[0].ats = time.mktime(datetime.datetime.now().timetuple())
    self.seekftbln(self.svfs,0)
    self.ftbl[0].tofile(self.svfs)
  except IOError:
   self.CloseSVFS()
   raise self.SVFSIOError(6,'Read/Write failed')
  return 0
