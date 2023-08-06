##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Pickle support functions for fssync.

The functions here generate pickles that understand their location in
the object tree without causing the entire tree to be stored in the
pickle.  Persistent objects stored inside the outermost object are
stored entirely in the pickle, and objects stored outside by outermost
object but referenced from within are stored as persistent references.
The parent of the outermost object is treated specially so that the
pickle can be 'unpacked' with a new parent to create a copy in the new
location; unpacking a pickle containing a parent reference requires
passing an object to use as the parent as the second argument to the
`loads()` function.  The name of the outermost object is not stored in
the pickle unless it is stored in the object.

>>> from zope.location.tests import TLocation
>>> root = TLocation()
>>> zope.interface.directlyProvides(root, IContainmentRoot)
>>> o1 = DataLocation('o1', root, 12)
>>> o2 = DataLocation('o2', root, 24)
>>> o3 = DataLocation('o3', o1, 36)
>>> o4 = DataLocation('o4', o3, 48)
>>> o1.foo = o2

>>> s = dumps(o1)
>>> c1 = loads(s, o1.__parent__, o1.__parent__)
>>> c1 is not o1
1
>>> c1.data == o1.data
1
>>> c1.__parent__ is o1.__parent__
1
>>> c1.foo is o2
1
>>> c3 = c1.o3
>>> c3 is o3
0
>>> c3.__parent__ is c1
1
>>> c3.data == o3.data
1
>>> c4 = c3.o4
>>> c4 is o4
0
>>> c4.data == o4.data
1
>>> c4.__parent__ is c3
1

$Id: fspickle.py 73003 2007-03-06 10:34:19Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import cPickle
from cStringIO import StringIO

import zope.interface
from zope import location
from zope.location.interfaces import ILocation
from zope.location.traversing import LocationPhysicallyLocatable
from zope.location.tests import TLocation
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.interfaces import ITraverser

PARENT_MARKER = ".."

# We're not ready to use protocol 2 yet; this can be changed when
# zope.xmlpickle.ppml gets updated to support protocol 2.
PICKLE_PROTOCOL = 1


def dumps(ob):
    parent = getattr(ob, '__parent__', None)
    if parent is None:
        return cPickle.dumps(ob)
    sio = StringIO()
    persistent = ParentPersistentIdGenerator(ob)
    p = cPickle.Pickler(sio, PICKLE_PROTOCOL)
    p.persistent_id = persistent.id
    p.dump(ob)
    data = sio.getvalue()
    return data

def loads(data, location, parent=None):
    sio = StringIO(data)
    if parent is None:
        persistent = PersistentLoader(location)
    else:
        persistent = ParentPersistentLoader(location, parent)
    u = cPickle.Unpickler(sio)
    u.persistent_load = persistent.load
    return u.load()


class ParentPersistentIdGenerator(object):
    """

    >>> from zope.location.tests import TLocation
    >>> root = TLocation()
    >>> zope.interface.directlyProvides(root, IContainmentRoot)
    >>> o1 = TLocation(); o1.__parent__ = root; o1.__name__ = 'o1'
    >>> o2 = TLocation(); o2.__parent__ = root; o2.__name__ = 'o2'
    >>> o3 = TLocation(); o3.__parent__ = o1; o3.__name__ = 'o3'
    >>> root.o1 = o1
    >>> root.o2 = o2
    >>> o1.foo = o2
    >>> o1.o3 = o3

    >>> gen = ParentPersistentIdGenerator(o1)
    >>> gen.id(root)
    '..'
    >>> gen.id(o2)
    u'/o2'
    >>> gen.id(o3)
    >>> gen.id(o1)

    >>> gen = ParentPersistentIdGenerator(o3)
    >>> gen.id(root)
    u'/'

    """

    def __init__(self, top):
        self.location = top
        self.parent = getattr(top, "__parent__", None)
        self.root = LocationPhysicallyLocatable(top).getRoot()

    def id(self, object):
        if ILocation.providedBy(object):
            if location.inside(object, self.location):
                return None
            elif object is self.parent:
                # emit special parent marker
                return PARENT_MARKER
            elif location.inside(object, self.root):
                return LocationPhysicallyLocatable(object).getPath()
            elif object.__parent__ is None:
                return None
                
            raise ValueError(
                "object implementing ILocation found outside tree")
        else:
            return None


class PersistentLoader(object):

    def __init__(self, context):
        locatable = LocationPhysicallyLocatable(context)
        __traceback_info__ = (context, locatable)
        self.root = locatable.getRoot()
        self.traverse = ITraverser(self.root).traverse

    def load(self, path):
        if path[:1] == u"/":
            # outside object:
            if path == "/":
                return self.root
            else:
                return self.traverse(path[1:])
        raise ValueError("unknown persistent object reference: %r" % path)


class ParentPersistentLoader(PersistentLoader):

    def __init__(self, context, parent):
        self.parent = parent
        PersistentLoader.__init__(self, context)

    def load(self, path):
        if path == PARENT_MARKER:
            return self.parent
        else:
            return PersistentLoader.load(self, path)
    

class DataLocation(TLocation):
    """Sample data container class used in doctests."""

    def __init__(self, name, parent, data):
        self.__name__ = name
        self.__parent__ = parent
        if parent is not None:
            setattr(parent, name, self)
        self.data = data
        super(DataLocation, self).__init__()
