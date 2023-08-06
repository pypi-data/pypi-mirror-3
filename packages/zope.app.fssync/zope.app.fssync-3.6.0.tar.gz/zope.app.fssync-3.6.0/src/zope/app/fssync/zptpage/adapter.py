##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
from zope.interface import implements
from zope.fssync import synchronizer
from zope.fssync import interfaces

class ZPTPageAdapter(synchronizer.FileSynchronizer):
    """Synchronizer adapter for ZPT page objects.
    """
    implements(interfaces.IFileSynchronizer)

    def dump(self, writeable):
        writeable.write(self.context.getSource())

    def load(self, readable):
        # Convert the data to Unicode, since that's what ZPTPage wants;
        # it's normally read from a file so it'll be bytes.

        # Sometimes we cannot communicate an encoding. Zope's default is UTF-8,
        # so use it.
        data = readable.read()
        self.context.setSource(data.decode('UTF-8'))
