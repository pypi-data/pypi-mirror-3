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
"""Filesystem synchronization support for zope.dublincore.

$Id: adapter.py 76675 2007-06-14 07:05:37Z oestermeier $
"""
__docformat__ = 'restructuredtext'


from zope import interface
from zope import component
from zope.fssync import synchronizer

class ZDCAnnotationDataSynchronizer(synchronizer.DefaultSynchronizer):
    """A default serializer which can be registered with less strict
    permissions, since DC metadata are rarely security related.
    """

