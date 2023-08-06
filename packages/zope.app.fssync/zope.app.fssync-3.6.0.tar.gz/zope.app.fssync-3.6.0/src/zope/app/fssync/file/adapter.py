##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Filesystem synchronization support.

$Id: adapter.py 76675 2007-06-14 07:05:37Z oestermeier $
"""
__docformat__ = 'restructuredtext'


from zope import interface
from zope import component
from zope.fssync import synchronizer
from zope.fssync import interfaces

from zope.app.file import file


class FileSynchronizer(synchronizer.Synchronizer):
    """Adapter to provide a fssync serialization of a file.

    >>> sample = file.File('some data', 'text/plain')
    >>> sample.getSize()
    9
    
    >>> class Writeable(object):
    ...     def write(self, data):
    ...         print data

    >>> synchronizer = FileSynchronizer(sample)
    >>> synchronizer.dump(Writeable())
    some data
    >>> sample.data = 'other data'
    >>> synchronizer.dump(Writeable())
    other data
    
    >>> sorted(synchronizer.extras().items())
    [('contentType', 'text/plain')]
    
    If we deserialize the file we must use chunking
    in for large files:
    
    >>> class Readable(object):
    ...     size = file.MAXCHUNKSIZE + 1
    ...     data = size * 'x'
    ...     def read(self, bytes=None):
    ...         result = Readable.data[:bytes]
    ...         Readable.data = Readable.data[bytes:]
    ...         return result
    
    >>> synchronizer.load(Readable())
    >>> len(sample.data) == file.MAXCHUNKSIZE + 1
    True
    >>> sample.getSize() == file.MAXCHUNKSIZE + 1
    True

    """

    interface.implements(interfaces.IFileSynchronizer)

    def metadata(self):
        md = super(FileSynchronizer, self).metadata()
        if not self.context.contentType or \
            not self.context.contentType.startswith('text'):
            md['binary'] = 'true'
        return md
        
    def dump(self, writeable):
        data = self.context._data
        if isinstance(data, file.FileChunk):
            chunk = data
            while chunk:
                writeable.write(chunk._data)
                chunk = chunk.next
        else:
            writeable.write(self.context.data)

    def extras(self):
        return synchronizer.Extras(contentType=self.context.contentType)

    def load(self, readable):
        chunk = None
        size = 0
        data = readable.read(file.MAXCHUNKSIZE)
        while data:
            size += len(data)
            next = file.FileChunk(data)
            if chunk is None:
                self.context._data = next
            else:
                chunk.next = next
            chunk = next
            data = readable.read(file.MAXCHUNKSIZE)
        self.context._size = size
        if size < file.MAXCHUNKSIZE:
            self.context.data = self.context.data

