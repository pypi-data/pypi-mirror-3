
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
"""Filesystem synchroniation support for `zope.app.module`.

$Id: adapter.py 76675 2007-06-14 07:05:37Z oestermeier $
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements

from zope.fssync import synchronizer
from zope.fssync import interfaces


class ModuleAdapter(synchronizer.FileSynchronizer):

    implements(interfaces.IFileSynchronizer)

    def dump(self, writeable):
        writeable.write(self.context.source)

    def load(self, readable):
        self.context.update(readable.read())

    def extras(self):
        return synchronizer.Extras(name=self.context.name)
